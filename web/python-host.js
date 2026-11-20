window.pythonResult=null;window.pythonReady=false;window.pythonError=null;
window.pythonWorker=new Worker('/static/python-worker.js');
window.pythonWorker.onmessage=event=>{if(event.data.type==='ready')window.pythonReady=true;else if(event.data.type==='bootstrap-error')window.pythonError=event.data.error;else if(event.data.type==='result')window.pythonResult=event.data};
