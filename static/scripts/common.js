String.prototype.trim = function(){
    return this.replace(/(^\s*)|(\s*$)/g, "");
}

String.prototype.ltrim = function(){
    return this.replace(/(^\s*)/g,"");
}

String.prototype.rtrim = function(){
    return this.replace(/(\s*$)/g,"");
}

function valid_email(email) {
    var patten = new RegExp(/^[a-zA-Z]((\w*\.\w*)|\w*)[a-zA-Z0-9]@(\w+\.)+[a-zA-Z]{2,}$/);
    return patten.test(email);
}

function valid_phone(phone) {
    var patten = new RegExp(/^13|14|15|18\d{9}$/);
    return patten.test(phone);
}

function validDateTime(datetime) {
    /* eg: 2013-09-01 10:03:05*/
    var reg = /^((([0-9]{3}[1-9]|[0-9]{2}[1-9][0-9]{1}|[0-9]{1}[1-9][0-9]{2}|[1-9][0-9]{3})-(((0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))|((0[469]|11)-(0[1-9]|[12][0-9]|30))|(02-(0[1-9]|[1][0-9]|2[0-8]))))|((([0-9]{2})(0[48]|[2468][048]|[13579][26])|((0[48]|[2468][048]|[3579][26])00))-02-29)) (20|21|22|23|[0-1]\d):[0-5]\d:[0-5]\d$/;
    if (datetime.trim() != "") {
        return reg.test(datetime.trim());
    }
    return false;
}

function validDateTime2(datetime) {
    /* eg: 2013-09-01 10:03*/
    var reg = /^((([0-9]{3}[1-9]|[0-9]{2}[1-9][0-9]{1}|[0-9]{1}[1-9][0-9]{2}|[1-9][0-9]{3})-(((0[13578]|1[02])-(0[1-9]|[12][0-9]|3[01]))|((0[469]|11)-(0[1-9]|[12][0-9]|30))|(02-(0[1-9]|[1][0-9]|2[0-8]))))|((([0-9]{2})(0[48]|[2468][048]|[13579][26])|((0[48]|[2468][048]|[3579][26])00))-02-29)) (20|21|22|23|[0-1]\d):[0-5]\d$/;
    if (datetime.trim() != "") {
        return reg.test(datetime.trim());
    }
    return false;
}

function validDate(date) {
    /* eg: 2013-09-01 */
    var reg = new RegExp("^(?:(?:([0-9]{4}(-|\/)(?:(?:0?[1,3-9]|1[0-2])(-|\/)(?:29|30)|((?:0?[13578]|1[02])(-|\/)31)))|([0-9]{4}(-|\/)(?:0?[1-9]|1[0-2])(-|\/)(?:0?[1-9]|1\\d|2[0-8]))|(((?:(\\d\\d(?:0[48]|[2468][048]|[13579][26]))|(?:0[48]00|[2468][048]00|[13579][26]00))(-|\/)0?2(-|\/)29))))$");
    if (date.trim() != "") {
        return reg.test(date.trim());
    }
    return false;
}

Date.prototype.format = function(format,now) {
    /* eg:format="yyyy-MM-dd hh:mm:ss N"; */
    var d = now ? (new Date(Date.parse(now.replace(/-/g,   "/")))) : this;
    var o = {
        "M+" : d.getMonth() + 1, // month
        "d+" : d.getDate(), // day
        "h+" : d.getHours(), // hour
        "m+" : d.getMinutes(), // minute
        "s+" : d.getSeconds(), // second
        "q+" : Math.floor((d.getMonth() + 3) / 3), // quarter
        "N+" : ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"][d.getDay()],
         "S" : d.getMilliseconds()// millisecond
    }
    if (/(y+)/.test(format)) {
        format = format.replace(RegExp.$1, (d.getFullYear() + "").substr(4 - RegExp.$1.length));
    }
    for (var k in o) {
        if (new RegExp("(" + k + ")").test(format)) {
            format = format.replace(RegExp.$1, RegExp.$1.length == 1 ? o[k] : ("00" + o[k]).substr(("" + o[k]).length));
        }
    }
    return format;
}
