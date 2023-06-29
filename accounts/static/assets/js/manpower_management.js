var a = NaN
var bus_count_info
var bus_current_page = 0
var bus_next = null
var bus_prev = null
var bus_first_included=true
var bus_last_included=true
var bus_total_page = 0
var bus_pages = []

$(window).on('load', function () {
    hideloader();
    if (window.location.pathname == "/list/employee" ){
        get_employee_data(1)
    }
    if (window.location.pathname == "/manpower/management"){
        get_employee_data(1)
        roster_data()
        get_chart_data()
        leave_data()
    }
    a = parseInt(location.pathname.split('/')[2])
    let b = location.pathname.split('/')[3]
    if (isNaN(a) == false) {
        get_employee_detail(a, b)
    }
});

function get_chart_data(){
//    On Ajax call will get the data from the api for chart
    loader();
     $.ajax({
        url : '/api/v1/roaster/list/roster_data/',
        type : 'get',
        dataType:'json',
        success : function(data) {
            hideloader();
         chart_series_data(data)
         set_analytics(data)
        },
         error: function(error) {
             hideloader();
        }
    });
}

function chart_series_data(data){
//  here data will set for the pie chart showing on the dashbiard.
    data = [{y:data.active_roster, color: '#90ED7D'}, {y: data.inactive_roster , color:'#3c77c3'}]

    Highcharts.chart('chart_container', {
    title:{
        text:''
    },

      chart: {
        type: 'pie',
        animation: false,
        backgroundColor: "#fbfbfb"
      },

      plotOptions: {
        pie: {

          borderWidth: 5,

          dataLabels: {
            enabled: false
          }
        },
        series: {
          states: {
            hover: {
              enabled: false
            }
          }
        }
      },
      tooltip: {
      enabled:false,
      animation: false
      },

      series: [{
        data:data
      }]

    });
    $('.highcharts-credits').hide()
}


function roster_data(){
//    ajax will get the list of  roster.
    loader();
    $.ajax({
        url: '/api/v1/roaster/list/',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            hideloader();
            roster_dashboard(data)
        },
        error: function (error) {
            hideloader();
        }
    });

}
function leave_data(){
//  get the list of leaves
    loader();
    $.ajax({
        url: '/api/v1/list/leaves/',
        type: 'get',
        dataType: 'json',
        success: function (data) {
             hideloader();   
            leave_dashboard (data)
        },
        error: function (error) {
            hideloader();
        }
    });

}
function leave_dashboard(data){
//  prepare a string and append in html of leave table.
    $(".leave").empty()
    length = data.length

    if (length != 0){
        for (i=length-1;i>=0;i--){
            stri='<tr><td class="left-content leave-img"><div class="leave-block leave-user"><span class="profile-blk"><img src="'+(( data[i].profile_pic != '' &&  data[i].profile_pic != null)  ? data[i].profile_pic :'/static/assets/images/default-Image.jpg')+'" width="32" height="32" alt="User-leave"></span></div><div class="leave-block"><div class="drkblue-txt">'+ data[i].name +'</div><div>Emp. Id: '+ data[i].employee_id +'</div></div></td>'+
                '<td class="text-right right-content phone-view"><div>Phone:</div><div class=""> '+ (( data[i].contact != '' &&  data[i].contact != null) ?  data[i].contact : 'NA' ) +'</div></td><td class="text-right right-content web-view"><div class="top-spc">Phone: '+ (( data[i].contact != '' &&  data[i].contact != null) ?  data[i].contact : 'NA' ) +'</td></tr>'
                  $(".leave").append(stri);
        }
    }
    else{
        $(".no-leave").append('<div class="center-txt">No Record Found.</div>');
    }
}



function roster_dashboard(data){
//  Roster table data will append here.
    $(".all-roster").empty();
    stri = ''
    result_len= (data.length)
    for (i=result_len-1;i>=0;i--){
        stri='<tr><td class="drkblue-txt">'+ data[i].name +'</td><td>Roster No: '+ data[i].roster_no +'</td><td> '+ data[i].members.length +' member(s)</td><td>Time: '+ convert_time(data[i].from_time) +' To '+ convert_time(data[i].to_time) +'</td></tr>'
        $(".all-roaster").append(stri);
    }
    if (result_len == 0){
        $(".no-roster").append('<div class="center-txt">No Record Found.</div>');
    }
    $(".inactive-rosater").empty();
    var count = 0
    for (i=result_len-1;i>=0;i--){
        if (data[i].status == '2'){
            count =count + 1
            stri='<tr><td class="left-content"><div class="drkblue-txt">'+ data[i].name +'</div><div>Roster No: '+ data[i].roster_no +'</div></td>'+
                '<td class="text-right right-content"><div class="drkblue-txt">'+ data[i].members.length +' members</div><div>Time: '+ convert_time(data[i].from_time) +' To '+ convert_time(data[i].to_time) +'</div></td></tr>'
            $(".inactive-rosater").append(stri);
        }

    }
    if (count==0){
        $(".inactive-rosater").empty();
        $(".inactive-rosater").append('<div class="center-txt">No Record Found.</div>');
    }
}


function convert_time(time){
    time = time.split(':'); // convert to array
    // fetch
    var hours = Number(time[0]);
    var minutes = Number(time[1]);
    var seconds = Number(time[2]);
    // calculate
    var timeValue;
    if (hours > 0 && hours <= 12) {
      timeValue= "" + hours;
    } else if (hours > 12) {
      timeValue= "" + (hours - 12);
    } else if (hours == 0) {
      timeValue= "12";
    }
    timeValue += (minutes < 10) ? ":0" + minutes : ":" + minutes;  // get minutes
//    timeValue += (seconds < 10) ? ":0" + seconds : ":" + seconds;  // get seconds
    timeValue += (hours >= 12) ? " PM" : " AM";  // get AM/PM'
    return timeValue
}

$(".previous-icon").click(function(){ get_employee_data(bus_current_page - 1); });
$(".next-icon").click(function(){ get_employee_data(bus_current_page + 1); });

function get_employee_detail(id, b) {
//  get the emplyee details on the basis of web page open.
    loader();
    if (b != '') {
        $.ajax({
            url: '/api/v1/user/' + id + '/',
            type: 'get',
            dataType: 'json',
            success: function (data) {
                hideloader();
                patch_details(data)

            },
            error: function (error) {
                hideloader();
            }
        });
    }
    else {
        $.ajax({
            url: '/api/v1/registration/' + id + '/',
            type: 'get',
            dataType: 'json',
            success: function (data) {
                hideloader();
                patch_form(data)
            },
            error: function (error) {
                hideloader();
            }
        });
    }
}

function patch_form(data) {
//   patch the data in form edit form
    $("input[name='first_name']").val(data.first_name)
    $("input[name='last_name']").val(data.last_name)
    $("input[name='email']").val(data.email)
    $("input[name='contact']").val(data.contact)
    $("select[name='department']").val(data.department)
    $.getJSON("/getDesignation/",{id: data.department}, function(j){
         var options = '<option value="">Select Designation</option>';
         for (var i = 0; i < j.length; i++) {
             options += '<option value="' + j[i].id + '">' + j[i].designation_name + '</option>';
         }
         $("select#designation").html(options);
         $("select[name='designation']").val(data.designation)
     });
     console.log(data.joining_date)
    if (data.joining_date){
        $("input[name='joining_date']").val(get_date(data.joining_date))
    }
    $("input[name='employee_id']").val(data.employee_id)
    if (!data.profile_picture == 'null' || !data.profile_picture == ''){
        x = data.profile_picture.split('/')
        $('.profile_picture').empty()
        $('.profile_picture').append(x[x.length - 1])
        $(".profile_picture").css("color", "rgb(61 70 78)")
    }if (!data.driving_licence == 'null' || !data.driving_licence == ''){
        z = data.driving_licence.split('/')
        $('.driving').empty()
        $('.driving').append(z[z.length - 1])
        $(".driving").css("color", "rgb(61 70 78)")
    }if (!data.id_proof == 'null' || !data.id_proof == ''){
        w = data.id_proof.split('/')
        $('.proof').empty()
        $('.proof').append(w[w.length - 1])
        $(".proof").css("color", "rgb(61 70 78)")
    }
}
function get_date(date){
    return  moment(date).format('DD/MM/YYYY');
}
function patch_details(data) {
//    patch the data in the detail page.
    if (data.profile_picture != null){
        $("#profile")[0].src = data.profile_picture
    }
    $("#first_name").text(data.first_name)
    $("#last_name").text(data.last_name)
    $("#employee_id").text(data.employee_id)
    $("#email").text(data.email)
    $("#contact").text(((data.contact != '' && data.contact != null) ? data.contact : 'NA' ))
    $("#department").text(data.department)
    $("#designation").text(data.designation)
    $("#joining_date").text(data.joining_date)
    $("#status").text(get_status(data.is_active))
    $('#edit_button').attr("href", '/employee/'+data.id)
    if (data.driving_licence != null){
        $(".driving_licence").append('<img class="img-fluid" src='+ data.driving_licence +' width="160" height="89" alt="Driving License">')
    }
    else{
        $(".driving_licence").append('<img class="img-fluid" src="/static/assets/images/default-Image.jpg" width="160" height="89" alt="Driving License">')
    }
    if(data.id_proof != null){
        $(".id_proof").append('<img class="img-fluid" src='+ data.id_proof +' width="160" height="89" alt="Id Proof">')
    }
    else{
        $(".id_proof").append('<img class="img-fluid" src="/static/assets/images/default-Image.jpg" width="160" height="89" alt="Id Proof">')
    }
}



function edit_form() {
//  edit form submit
    if ($("#add_employee_form").valid()) {
        var data = $("#add_employee_form")[0]
        var form_data = new FormData(data)
        loader();
        $.ajax({
            url: '/api/v1/registration/' + a + '/',
            type: 'put',
            data: form_data,
            cache: false,
            processData: false,
            contentType: false,
            success: function (data) {
                hideloader();
                window.setTimeout(function(){
                    location.href = '/list/employee'
                }, 1000);
                $('.alert-success').show().delay(1500)
                $('#succ-msg').text('Employee edited successfully.')
            },
            error: function (data) {
                hideloader();
                var i = 0
                for (var key in data.responseJSON) {
                    if (i == 0) {
                        $('.alert-danger').show().delay(1500)
                        $('#error_txt').text(data.responseJSON[key][0])
                    }
                    i = i + 1
                }
            }
        });
    }
}

$('#profile_picture').on('change', function () {
    if (this.files.length > 0) {
        $(".profile_picture").empty()
        $(".profile_picture").append(this.files[0].name)
        $(".profile_picture").css("color", "#415c73")
    }
    else {
        $(".profile_picture").empty()
        $(".profile_picture").append("Accepted: jpg, jpeg, png")
        $(".profile_picture").css("color", "#97abbc")
    }
});

$('#driving_licence').on('change', function () {
    if (this.files.length > 0) {
        $(".driving").empty()
        $(".driving").append(this.files[0].name)
        $(".driving").css("color", "#415c73")
    }
    else {
        $(".driving").empty()
        $(".driving").append("Accepted: jpg, jpeg, png")
        $(".driving").css("color", "#97abbc")
    }
});

function create_user() {
//  Create a user.
    if ($("#add_employee_form").valid()) {
        var data = $("#add_employee_form")[0]
        var form_data = new FormData(data)
        loader();
        $.ajax({
            url: '/api/v1/registration/',
            type : 'POST',
            data : form_data,
            cache: false,
            processData: false,
            contentType: false,
            success: function (data) {
                hideloader();
                $("#add_employee_form")[0].reset();
                $("#emp_id").text(data.employee_id)
                $("#joning").text(get_date(data.joining_date))
                $('#myModal').modal('toggle');
            },
            error: function (data) {
                hideloader();
               var i = 0
               for (var key in data.responseJSON) {
                   if (i ==0){
                    $('.alert-danger').show().delay(1000)
                    $('#error_txt').text(data.responseJSON[key][0])
                   }
                   i = i +1

                }
            }
        });
    }
}
function employee_search(search){
    if (window.location.pathname == "/list/employee"){
        $.ajax({
            url : '/api/v1/registration/?search='+search.value,
            type : 'get',
            dataType:'json',
            success : function(data) {
                    bus_total_page = Math.ceil(data['count']/8)
                    pagination(data)
                    employee_table(data)
                },
            error: function (data) {
                hideloader();
            }
        });
    }
    else{
        $.ajax({
            url : '/api/v1/list/user/?search='+search.value,
            type : 'get',
            dataType:'json',
            success : function(data) {
                    bus_total_page = Math.ceil(data['count']/4)
                    pagination(data)
                    employee_dashboard(data)
                },
            error: function (data) {
                hideloader();
            }
        });
    }
//    api/v1/user/?search=deepak
}
function get_employee_data(page){
    if (window.location.pathname == "/list/employee"){
        loader();
        $.ajax({
            url : '/api/v1/registration/?page='+page,
            type : 'get',
            dataType:'json',
            success : function(data) {
                hideloader();
                bus_total_page = Math.ceil(data['count']/8)
                pagination(data)
                employee_table(data)
            },
            error: function (data) {
                hideloader();
            }
        });
    }
    if (window.location.pathname == "/manpower/management"){
        loader();
        $.ajax({
            url : '/api/v1/list/user/?page='+page,
            type : 'get',
            dataType:'json',
            success : function(data) {
                hideloader();
                bus_total_page = Math.ceil(data['count']/4)
                pagination(data)
                employee_dashboard(data)
            },
            error: function (data) {
                hideloader();
            }
        });
    }
}
function pagination(data){
    bus_count_info = data['count']
    bus_current_page = data['current']
    bus_next = data['next']
    bus_prev = data['previous']
    bus_first_included = true
    bus_last_included = true

    bus_pages = []
    for (var i=bus_current_page-2; i<=bus_current_page+2; i++) {
      if(i>0 && i<=bus_total_page){
        bus_pages.push(i);
      }
    }
    if(bus_current_page-2>1){
      bus_first_included=false
    }
    if(bus_current_page+2<bus_total_page){
      bus_last_included=false
    }
    $(".next-icon-list").empty();
    for(var item of bus_pages){
        $(".next-icon-list").append('<li><a class="element" href="javascript:get_employee_data('+item+');" id="'+item+'" title="">'+(item)+'</a></li>')
        if (bus_current_page == item){
            $("#"+item)[0].parentNode.classList.add("active")
        }
    }
}


function employee_table(data){
    console.log(data)
    $(".table-block").empty();
    $(".no-data").empty();
    stri = ''
    result_len= data.results.length
    if (result_len !=0){
        for (i=result_len-1;i>=0;i--){
            var contact = (data.results[i].contact != '' && data.results[i].contact != null)? data.results[i].contact : "NA"
            var driving_licence = (  data.results[i].driving_licence != '' && data.results[i].driving_licence != null) ?  data.results[i].driving_licence :  ''
            var id_proof = (  data.results[i].id_proof != '' && data.results[i].id_proof != null) ?  data.results[i].id_proof :  ''
            var joining_date = (  data.results[i].joining_date != '' && data.results[i].joining_date != null) ?  data.results[i].joining_date :  ''
            stri1 = ''
            if (driving_licence != ''){
                var stri1 = '<a href="'+data.results[i].driving_licence+'" target="_blank" title="View" class="box blue-txt">'+ check_licence(driving_licence) +'</a>'
            }
            stri2 = ''
//            if (id_proof != ''){
//                var stri2 = '<a href="javascript:void(0);" title="View" class="box green-txt">'+ check_proof(id_proof) +'</a>'
//            }
            stri='<tr class="table-block">'+
                '<td>'+ data.results[i].first_name +' '+ data.results[i].last_name +'</td><td>'+ data.results[i].employee_id +'</td><td>'+ data.results[i].email +'</td>'+
                '<td>'+ contact +'</td><td>'+ joining_date +'</td><td>'+ data.results[i].department +'</td><td>'+ data.results[i].designation +'</td>'+
                '<td>'+ stri1 +''+stri2+''+
                '</td><td class="actions"><a href="/detail/'+ data.results[i].id +'/employee/" onclick="myFunction()" title="View" class="icon-blk green-block">'+
                '<i class="fas fa-eye"></i></a><a href="/employee/'+ data.results[i].id +'/" title="Edit" class="blue-block icon-blk">'+
                '<i class="fas fa-pen"></i></a></td></tr>'
            $(".header-row").after(stri);
        }
    }
    else{
        $(".no-data").append('<div class="center-txt">No Record Found.</div>');
    }
}

function get_class(status){
    if (status == "1"){
        return "green-badge"
    }
    else if(status == "0"){
        return 'red-badge'
    }
}
function employee_dashboard(data){
    $(".table-block").empty();
    $(".no-found").empty();
    stri = ''
    result_len= data.results.length
    if (result_len > 0){
        for (i=result_len-1;i>=0;i--){
            var contact = (data.results[i].contact != '' && data.results[i].contact != null)? data.results[i].contact : "NA"
            var joining_date = (  data.results[i].joining_date != '' && data.results[i].joining_date != null) ?  data.results[i].joining_date :  ''
            stri='<tr class="table-block">'+
                '</label></td><td><a href="/detail/'+data.results[i].id+'/employee/" class="icon-blk green-block" title="View Detail">'+
                '<i class="fas fa-eye"></i></a><a href="/employee/'+data.results[i].id+'/" class="blue-block icon-blk" title="Edit"><i class="fas fa-pen"></i></a></td>'+
                '<td>'+ data.results[i].first_name +' '+ data.results[i].last_name +'</td><td>'+ data.results[i].employee_id +'</td><td>'+ data.results[i].email +'</td>'+
                '<td>'+ contact +'</td><td>'+ data.results[i].department +'</td><td>'+ data.results[i].designation +'</td><td><span >'+ joining_date +'</span></td>'

            $(".header-row").after(stri);
        }
    }
    else{
        $(".no-found").append('<div class="center-txt">No Record Found.</div>');
    }
}


function get_status(status){
    if (status == true){
        return "Active"
    }
    else{
        return "Inactive"
    }
}
function check_licence(d){
    if (d != ''){
        return 'dl'
    }
    else{
        return ''
    }
}
function check_proof(i){
    if (i != ''){
        return 'id'
    }
    else{
        return ''
    }
}

jQuery.validator.addMethod("lettersonly", function (value, element) {
    return this.optional(element) || /^[a-z]+$/i.test(value);
}, "Letters only please");
jQuery.validator.addMethod("numbersonly", function (value, element) {
    return this.optional(element) || /^[0-9]+$/i.test(value);
}, "Numbers only please");
jQuery.validator.addMethod("regexs", function(value, element) {
  return this.optional(element) || /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(value);
}, "not a valid email.");
 jQuery.validator.addMethod("filetype", function(value, element) {
    var types = ['jpeg', 'jpg', 'png'],
        ext = value.replace(/.*[.]/, '').toLowerCase();

    if (types.indexOf(ext) !== -1 || value== '') {
            //$("#city_banner-error").html('');
        return true;
    }

    return false;
    },
  "Please select allowed file"
  );
   $.validator.addMethod("filetypes", function(value, element) {
    return this.optional(element) || /\\([a-z0-9])*\.(png|jpg|jpeg)/i.test(value);
  }, "Incorect file type");

$('input[name=contact]').usPhoneFormat()
$("#add_employee_form").validate({
    errorPlacement: function errorPlacement(error, element) {
        element.after(error);
    },
    errorClass: 'custom-error',
    rules: {
        first_name: {
            required: true,
            lettersonly: true,
            minlength: 1,
            maxlength: 30
        },
        last_name: {
            required: true,
            lettersonly: true,
            maxlength: 30
        },
        email: {
            required: true,
            maxlength: 50,
            regexs: true,
            remote:{
                url: '/api/v1/registration/check_user/',
                type: "get",

            }
        },
        employee_id: {
            required: true,
            maxlength: 7,
             remote:{
                url: '/api/v1/registration/check_user/',
                type: "get",

            }
        },
        contact: {
            numbersonly: false,
            minlength : 12,
            maxlength: 12
        },
        department: {
            required: true,
        },
        designation: {
            required: true,
        },
        joining_date: {
            required: true
        },
        id_proof:{
            filetype: true
        },
        driving_licence:{
            filetype: true
        },
        profile_picture:{
            filetype: true
        },

    },
    messages: {
        first_name: {
            required: 'Please enter the first name. ',
            lettersonly: ' Please enter the valid first name. ',
            maxlength: 'First name should be less than equal to 30 characters.'
        },
        last_name: {
            required: 'Please enter the last name.',
            lettersonly: 'Please enter the valid last name.',
            maxlength: 'Last name should be less than equal to 30 characters.'
        },
        email: {
            required: 'Please enter email address.',
            maxlength: 'Email can have at most 50 characters.',
            regexs: 'Please enter a valid email address.',
            remote: 'User with this Email already exists.'
        },
        employee_id: {
            required: 'Please enter employee Id.',
            maxlength: 'Employee Id can have at most 7 characters.',
            remote: 'User with this Employee Id already exists.'
        },
        contact: {
            numbersonly: "Please enter the digits only.",
            minlength: "Contact should be at least 10 digits.",
            maxlength: 'Contact should be less than equal to 10 digits.'
        },
        department: {
            required: 'Please select a department.',
        },
        designation: {
            required: 'Please select a designation',
        },
        joining_date: {
            required: 'Please enter the joining date.'
        },


    },
});

function validate_file(file){
    const validImageTypes = ['image/jpg', 'image/jpeg', 'image/png'];
        var name=$(file).attr('id')
            if (!validImageTypes.includes(file.files[0].type)){
                $("#"+name+"1").text("Please select Only .jpg, .png and .jpeg format.")
                 file_upload = false
                }
            else{
                $("#"+name+"1").text('')
            }


}

$('#id_proof, #profile_picture, #driving_licence').on('change', function(){
validate_file(this)
});

function export_data(email=false, file_type='pdf') {
//  export file data of current table
    var url ='/api/v1/export/employees?file_type='+file_type
    if (email) {
        url=url+'&email'
        loader();
        $.ajax({
            url : url,
            type : 'get',
            dataType:'json',
            success : function(data) {
                hideloader();
            },
             error: function(error) {
                 hideloader();
            }
        });
    }
    else {
        window.open(url)
    }
    
}

function set_analytics(data){
// set the analytics on dashboard

if (data.last_month > data.this_month){
$('#text2').addClass('green-txt')
$('#text1').addClass('orange-txt')
$('#text1').removeClass('green-txt')
$('#graph_data1').removeClass('greengraph-data')
$('#graph_data2').addClass('greengraph-data')
$('#graph_icon1').removeClass('green-graph-icon').addClass('orange-graph-icon')
$('#graph_icon2').addClass('green-graph-icon').removeClass('orange-graph-icon')
$('#arrow1').removeClass('green-arow').addClass('orange-arow')
$('#arrow2').addClass('green-arow')

}
}
$(function(){
    $(document).on('change', "select#department", function(){
        $.getJSON("/getDesignation/",{id: $(this).val()}, function(j){
             var options = '<option value="">Select Designation</option>';
             for (var i = 0; i < j.length; i++) {
                 options += '<option value="' + j[i].id + '">' + j[i].designation_name + '</option>';
             }
             $("select#designation").html(options);
         });
     });
    });

function loader(){
    $('.dynamic-loader').show()
    $('.overlay').show()
}
function hideloader(){
    $('.dynamic-loader').hide()
    $('.overlay').hide()
}