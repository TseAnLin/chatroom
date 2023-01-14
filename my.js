    const app = require('express')();
  const http = require('http').createServer(app);
  const io = require('socket.io')(http);

  app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
  });

  http.listen(3001, () => {
    console.log('listening on *:3000');
  });