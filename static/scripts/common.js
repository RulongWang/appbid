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

