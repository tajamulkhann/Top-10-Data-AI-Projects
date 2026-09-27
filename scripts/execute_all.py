"""Execute notebooks with an in-process IPython shell; retain actual MIME outputs.
No socket permissions or notebook server required. Errors stop the build.
"""
from pathlib import Path
import json,time,os,sys,subprocess
ROOT=Path(__file__).resolve().parents[1]
def run(path):
    import nbformat
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from IPython.core.interactiveshell import InteractiveShell
    from IPython.utils.capture import capture_output
    from IPython.display import display,Image
    import io
    shell=InteractiveShell.instance()
    def show(*args,**kwargs):
        for number in plt.get_fignums():
            fig=plt.figure(number);buf=io.BytesIO();fig.savefig(buf,format='png',bbox_inches='tight');display(Image(data=buf.getvalue()))
        plt.close('all')
    plt.show=show
    os.chdir(path.parent)
    nb=nbformat.read(path,as_version=4);start=time.time();count=0
    for c in nb.cells:
        if c.cell_type!='code':continue
        count+=1
        with capture_output(stdout=True,stderr=True,display=True) as captured:
            result=shell.run_cell(c.source,store_history=True)
        if result.error_before_exec or result.error_in_exec:
            raise RuntimeError(str(result.error_before_exec or result.error_in_exec))
        c.execution_count=count;c.outputs=[]
        if captured.stdout:c.outputs.append(nbformat.v4.new_output('stream',name='stdout',text=captured.stdout))
        if captured.stderr:c.outputs.append(nbformat.v4.new_output('stream',name='stderr',text=captured.stderr))
        for out in captured.outputs:
            c.outputs.append(nbformat.v4.new_output('display_data',data=out.data,metadata=out.metadata))
    nb.metadata['execution']={'method':'In-process IPython, isolated Python subprocess per notebook','python':sys.version.split()[0]}
    nbformat.validate(nb);nbformat.write(nb,path)
    return {'project':path.parent.name,'status':'passed','executed_cells':count,'output_count':sum(len(c.get('outputs',[])) for c in nb.cells),'seconds':round(time.time()-start,2)}
if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1] not in ['data-analytics','data-engineering']:
        print(json.dumps(run(Path(sys.argv[1]).resolve())))
    else:
        results=[]
        collection=sys.argv[1] if len(sys.argv)>1 else 'data-analytics'
        pattern='*/pipeline.ipynb' if collection=='data-engineering' else '*/analysis.ipynb'
        for path in sorted((ROOT/collection).glob(pattern)):
            p=subprocess.run([sys.executable,__file__,str(path)],text=True,capture_output=True)
            if p.returncode:print(p.stdout,p.stderr);raise SystemExit(p.returncode)
            result=json.loads(p.stdout.strip().splitlines()[-1]);results.append(result);print(result,flush=True)
        report=ROOT/'data-engineering/execution_report.json' if collection=='data-engineering' else ROOT/'execution_report.json'
        report.write_text(json.dumps(results,indent=2))
        assert len(results)==10
