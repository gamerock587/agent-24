/* Python executes in a fresh virtual filesystem; the parent blocks network after bootstrap. */
importScripts('/python-runtime/pyodide.js');
let python;
let output=[],errors=[];
let outputSize=0;
function append(target,line){outputSize+=line.length;if(outputSize>65536)throw new Error('Output budget exceeded');target.push(line)}
const ready=loadPyodide({indexURL:'/python-runtime/',stdout:line=>append(output,line),stderr:line=>append(errors,line)}).then(p=>{python=p;postMessage({type:'ready'})}).catch(e=>postMessage({type:'bootstrap-error',error:String(e)}));
self.onmessage=async event=>{
 await ready;output=[];errors=[];outputSize=0;
 try{
  python.FS.mkdirTree('/work');python.FS.writeFile('/work/input.json',JSON.stringify(event.data.inputs));
  await python.runPythonAsync(event.data.code);
  postMessage({type:'result',status:'completed',stdout:output.join('\n').slice(0,65536),stderr:errors.join('\n').slice(0,65536),exit_code:0});
 }catch(e){postMessage({type:'result',status:'failed',stdout:output.join('\n').slice(0,65536),stderr:String(e).slice(0,65536),exit_code:1})}
};
