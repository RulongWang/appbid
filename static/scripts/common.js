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
    var patten = new RegExp(/^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]+$/);
    return patten.test(email);
}

