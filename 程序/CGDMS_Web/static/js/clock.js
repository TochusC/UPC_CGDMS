function getTimeString() {
  var date = new Date();
  var hours = date.getHours();
  var minutes = date.getMinutes();
  var seconds = date.getSeconds();
  switch (hours) {
    case 0:
    case 1:
    case 2:
    case 3:
    case 4:
        ampm = '凌晨';
        break;
    case 5:
        ampm = "黎明";
        break;
    case 6:
        ampm = "拂晓";
        break;
    case 7:
    case 8:
        ampm = "清晨";
        break;
    case 9:
    case 10:
    case 11:
        ampm = "上午";
        break;
    case 12:
    case 13:
        ampm = "中午";
        break;
    case 14:
    case 15:
    case 16:
        ampm = "下午";
        break;
    case 17:
    case 18:
        ampm = "黄昏";
        break;
    case 19:
    case 20:
    case 21:
    case 22:
        ampm = "傍晚";
        break;
    case 23:
    case 24:
        ampm = "午夜";
        break;

  }
  hours = hours ? hours : 12; // the hour '0' should be '12'
  minutes = minutes < 10 ? '0'+minutes : minutes;
  seconds = seconds < 10 ? '0'+seconds : seconds;
  var timeString = ampm + ' ' + hours + ':' + minutes + ':' + seconds + ' '
  return timeString;
}
function updateClock() {
  var clock = document.getElementById('clock');
  clock.innerHTML = getTimeString();
}
setInterval(updateClock, 1000);