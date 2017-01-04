var form = document.forms["create-link"];

function durationOther() {
  if (!form["select-duration"].value) {
    document.getElementById("duration").style.display = "inline";
  } else {
    document.getElementById("duration").style.display = "none";
  }
}

function validateForm() {
  var url = form["url"].value;
  var alias = form["alias"].value;

  if (!url || !alias) {
    alert("Please enter a URL and alias.");
    return false;
  }

  if (!url.match(/(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/)) {
    alert("Make sure your URL is formatted as HTTP(S) or FTP.")
    return false;
  }

  if (!alias.match(/[a-zA-Z0-9\-]+/)) {
    alert("Your alias can contain letters, numbers, and dashes.")
    return false;
  }

  return true;
}
