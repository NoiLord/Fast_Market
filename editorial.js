/* Native details work without JS; deep links open the requested instruction. */
(()=>{function reveal(){let id;try{id=decodeURIComponent(location.hash.slice(1))}catch{return}if(!id)return;const target=document.getElementById(id);if(target?.tagName==='DETAILS')target.open=true}reveal();addEventListener('hashchange',reveal);})();
