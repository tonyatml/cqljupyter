import io
import os
import sys
import re
from ipykernel.kernelbase import Kernel
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import pandas as pd

from cqlshlib import cqlshmain, cql3handling, authproviderhandling
from cqlshlib.cqlshmain import setup_cqlruleset
from cqlshlib import cql3handling

__version__ = '2.0.0'

version_pat = re.compile(r'version (\d+(\.\d+)+)')


class CQLKernel(Kernel):
    implementation = 'cqljupyter'
    implementation_version = __version__
    banner = "CQL kernel"
    language = "CQL"
    language_info = {'name': 'CQL',
                     'codemirror_mode': 'sql',
                     'mimetype': 'text/x-cassandra',
                     'file_extension': '.cql'}

    @property
    def language_version(self):
        m = version_pat.search(self.banner)
        return m.group(1)

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)
        try:
            print("Initializing CQLKernel...")
            self.hostname = os.environ.get('CASSANDRA_HOSTNAME', 'localhost')
            self.port = int(os.environ.get('CASSANDRA_PORT', "9042"))
            self.user = os.environ.get('CASSANDRA_USER')
            self.pwd = os.environ.get('CASSANDRA_PWD')
            self.ssl = os.environ.get('CASSANDRA_SSL') == "True"
            print(f"Connecting to Cassandra at {self.hostname}:{self.port} user={self.user}")
            auth_provider = None
            if self.user and self.pwd:
                auth_provider = PlainTextAuthProvider(username=self.user, password=self.pwd)
            self.cluster = Cluster([self.hostname], port=self.port, auth_provider=auth_provider)
            self.cassandra_session = self.cluster.connect()
            self.last_result = None  # to store the result of the last query
            print("Cassandra connection established.")
        except Exception as e:
            print("Exception during kernel init:", e)
            import traceback
            traceback.print_exc()
            raise

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):
        clean_code = code.strip()
        if not clean_code:
            return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [], 'user_expressions': {}}

        try:
            # check if it's python code
            if clean_code.startswith('%%python'):
                # remove %%python mark
                python_code = clean_code[8:].strip()
                
                # create a string buffer to capture output
                import io
                import sys
                from contextlib import redirect_stdout
                import matplotlib.pyplot as plt
                
                # capture standard output
                output = io.StringIO()
                with redirect_stdout(output):
                    # execute python code
                    exec(python_code, {'_': self.last_result})
                
                # get output content
                output_text = output.getvalue()
                
                # if there is output, display it
                if output_text and not silent:
                    self.send_response(self.iopub_socket, 'stream', {
                        'name': 'stdout',
                        'text': output_text
                    })
                
                # check if there is a matplotlib chart
                if plt.get_fignums():
                    # convert the chart to html
                    import base64
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', bbox_inches='tight')
                    buf.seek(0)
                    img_str = base64.b64encode(buf.read()).decode('utf-8')
                    plt.close('all')  # clean the chart
                    
                    # send the chart
                    self.send_response(self.iopub_socket, 'display_data', {
                        'data': {'image/png': img_str},
                        'metadata': {}
                    })
                
                if not silent:
                    self.send_response(self.iopub_socket, 'stream', {
                        'name': 'stdout',
                        'text': '[INFO] For better syntax highlighting, set this cell to Python in the notebook UI.'
                    })
                
                return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [], 'user_expressions': {}}

            # check if it's a special command to get the result
            if clean_code == "_":
                if self.last_result is not None:
                    if not silent:
                        self.send_response(self.iopub_socket, 'execute_result', {
                            'data': {'text/plain': f'DataFrame with {len(self.last_result)} rows and {len(self.last_result.columns)} columns'},
                            'metadata': {},
                            'execution_count': self.execution_count
                        })
                    return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [], 'user_expressions': {}}
                else:
                    return {'status': 'error', 'ename': 'ValueError', 'evalue': 'No previous query result available', 'traceback': []}

            # only handle query statements, other like DDL/DML can be extended as needed
            result = self.cassandra_session.execute(clean_code)
            df = pd.DataFrame(result.all(), columns=result.column_names)
            self.last_result = df  # save the result to the instance variable
            
            if not silent:
                # send the html table of the DataFrame
                html = df.to_html()
                self.send_response(self.iopub_socket, 'display_data', {
                    'data': {'text/html': html},
                    'metadata': {}
                })
                # send a variable assignment message so the result can be used in subsequent cells
                self.send_response(self.iopub_socket, 'execute_result', {
                    'data': {'text/plain': f'DataFrame with {len(df)} rows and {len(df.columns)} columns'},
                    'metadata': {},
                    'execution_count': self.execution_count
                })
            return {'status': 'ok', 'execution_count': self.execution_count, 'payload': [], 'user_expressions': {}}
        except Exception as e:
            if not silent:
                self.send_response(self.iopub_socket, 'stream', {'name': 'stderr', 'text': str(e)})
            return {'status': 'error', 'ename': type(e).__name__, 'evalue': str(e), 'traceback': []}

    def do_complete(self, code, cursor_pos):
        code = code[:cursor_pos]

        default = {'matches': [], 'cursor_start': 0,
                   'cursor_end': cursor_pos, 'metadata': dict(),
                   'status': 'ok'}

        # Find the rightmost of blank, . , <, (

        index = max(code.rfind(' '),
                    code.rfind('.'),
                    code.rfind('<'),
                    code.rfind('('))
        completed = code[:index + 1]
        partial = code[index + 1:]

        matches = cql3handling.CqlRuleSet.cql_complete(completed, partial, cassandra_conn=self.cqlshell,
                                                       startsymbol='cqlshCommand')

        if not matches:
            return default

        tokens = code.replace(';', ' ').split()
        if not tokens:
            return default

        return {'matches': sorted(matches), 'cursor_start': cursor_pos - len(partial),
                'cursor_end': cursor_pos, 'metadata': dict(),
                'status': 'ok'}
