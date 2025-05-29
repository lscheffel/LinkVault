javascript:(function(){
    let url = window.location.href;
    let title = document.title;
    let timestamp = new Date().toISOString();
    let videoLinks = Array.from(document.querySelectorAll('a[href$=".mp4"], a[href$=".avi"], a[href$=".mkv"], a[href$=".webm"], a[href$=".mpg"]')).map(a => a.href);
    fetch('http://localhost:5005/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, url, timestamp, direct_links: videoLinks })
    })
    .then(res => res.json())
    .then(res => alert(res.message))
    .catch(err => alert('Erro: ' + err));
  })();