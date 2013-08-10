/**
 * Created with PyCharm.
 * User: rulongwang
 * Date: 8/10/13
 * Time: 8:35 AM
 * To change this template use File | Settings | File Templates.
 */

var categories = {
    "Automotive":[{"id":2,"name":"Cars"},
        {"id":3,"name":"Motorcycles"},
        {"id":4,"name":"Other Automotive"}],
    "Business":[{"id":6,"name":"Finance"},
        {"id":7,"name":"Forex"},
        {"id":8,"name":"Insurance"},
        {"id":9,"name":"Jobs"},
        {"id":10,"name":"Law"},
        {"id":110,"name":"Productivity"},
        {"id":11,"name":"Real Estate"},
        {"id":12,"name":"Other Business"}],
    "Design and Style":[{"id":14,"name":"Art"},
        {"id":15,"name":"Fashion"},
        {"id":16,"name":"Jewelry"},
        {"id":17,"name":"Logos"},
        {"id":18,"name":"Photography"},
        {"id":19,"name":"Tattoos"},
        {"id":20,"name":"Other Design and Style"}],
    "Education":[{"id":22,"name":"Colleges and Courses"},
        {"id":23,"name":"Languages"},
        {"id":24,"name":"Scholarships"},
        {"id":25,"name":"Study Guides and Tutorials"},
        {"id":26,"name":"Other Education"}],
    "Electronics":[{"id":28,"name":"Cameras"},
        {"id":29,"name":"Cell/Mobile Phones"},
        {"id":30,"name":"Computers"},
        {"id":31,"name":"Tablets"},
        {"id":32,"name":"Televisions"},
        {"id":33,"name":"Other Technology"}],
    "Entertainment":[{"id":35,"name":"Books"},
        {"id":36,"name":"Celebrities"},
        {"id":37,"name":"Film"},
        {"id":38,"name":"Humor"},
        {"id":39,"name":"Music"},
        {"id":40,"name":"Television"},
        {"id":41,"name":"Other Entertainment"}],
    "Family and Relationships":[{"id":47,"name":"Adult Products"},
        {"id":43,"name":"Baby"},{"id":44,"name":"Children"},
        {"id":45,"name":"Dating"},{"id":46,"name":"Wedding"},
        {"id":48,"name":"Other Family and Relationships"}],
    "Food and Drink":[{"id":50,"name":"Cooking and Recipes"},
        {"id":51,"name":"Drinks"},{"id":52,"name":"Food"},
        {"id":53,"name":"Other Food and Drink"}],
    "General Knowledge":[{"id":55,"name":"News and Current Affairs"},
        {"id":56,"name":"Politics and History"},
        {"id":57,"name":"Religion and Spirituality"},
        {"id":58,"name":"Science and Nature"},
        {"id":59,"name":"Other General Knowledge"}],
    "Health and Beauty":[{"id":61,"name":"Beauty"},
        {"id":62,"name":"Body Building"},
        {"id":63,"name":"Depression and Anxiety"},
        {"id":64,"name":"Diet and Nutrition"},
        {"id":65,"name":"Fitness"},
        {"id":66,"name":"Hair and Hair Loss"},
        {"id":67,"name":"Pregnancy"},
        {"id":68,"name":"Skin"},
        {"id":69,"name":"Sleep and Snoring"},
        {"id":70,"name":"Smoking"},
        {"id":71,"name":"Teeth"},
        {"id":72,"name":"Weight Loss"},
        {"id":73,"name":"Other Health and Beauty"}],
    "Hobbies and Games":[{"id":75,"name":"Gambling"},
        {"id":76,"name":"Games"},{"id":77,"name":"Gaming"},
        {"id":78,"name":"Other Hobbies and Games"}],
    "Home and Garden":[{"id":80,"name":"DIY"},
        {"id":81,"name":"Furniture"},
        {"id":82,"name":"Gardening"},
        {"id":83,"name":"Pets"},
        {"id":84,"name":"Toys"},
        {"id":85,"name":"Other Home and Garden"}],
    "Internet":[{"id":88,"name":"Coupons"},
        {"id":87,"name":"Domains"},
        {"id":89,"name":"Internet Marketing"},
        {"id":90,"name":"SEO"},
        {"id":91,"name":"Social Media"},
        {"id":92,"name":"Traffic Generation"},
        {"id":94,"name":"Web Development"},
        {"id":93,"name":"Website Design"},
        {"id":95,"name":"Other Internet"}],
    "Sports and Outdoor":[{"id":98,"name":"Boating"},
        {"id":99,"name":"Camping"},
        {"id":97,"name":"Cycling"},
        {"id":100,"name":"Football"},
        {"id":101,"name":"Golf"},
        {"id":102,"name":"Hunting"},
        {"id":103,"name":"Other Sports and Outdoor"}],
    "Travel":[{"id":106,"name":"Flights and Aviation"},
        {"id":107,"name":"Guides"},
        {"id":105,"name":"Hotels"},
        {"id":108,"name":"Vacation, Holiday and Resorts"},
        {"id":109,"name":"Other Travel"}]};
var current_cat = 0;

$('#parent_category').on('change', populateSubCategory);

$(document).ready(populateSubCategory);

function populateSubCategory()
{
  var cat = $('#category_id');
  cat.children().remove();
  _.each(categories[$('#parent_category').val()], function(cat_data)
  {
    var selected = (cat_data.id == current_cat) ? ' selected="selected" ' : '';
    cat.append('<option '+ selected +' value="'+ cat_data.id +'">' + cat_data.name + '</option>');
  });
}
