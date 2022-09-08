const express = require('express');
const path = require('path');

const app = express();

app.use(express.static(__dirname + '/../dist/optimizer-tool-frontend'));

app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  next();
});

app.get('/*', function(req,res) {
  res.sendFile(path.join(__dirname+'/../dist/optimizer-tool-frontend/index.html'));
});

app.listen(8080, () => console.log(`Front is being served!`));
