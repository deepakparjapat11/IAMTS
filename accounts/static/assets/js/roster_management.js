var member_options = []
var member_list = []
var monday = false
var tuesday = false
var wednesday = false
var thursday = false
var friday = false
var saturday = false
var sunday = false
var roster_count_info
var roster_current_page = 0
var roster_next = null
var roster_prev = null
var roster_first_included = true
var roster_last_included = true
var roster_total_page = 0
var roster_pages = []
var file_upload = false
var check_date = true
var empl_on_leave = []
var mem_in_roster = []
var selected_member = []

function status(status) {
    if (status == "1") {
        return "Active"
    }
    else if (status == "2") {
        return 'Inactive'
    }
}

function get_user_list(dept=null){
   var api_url = '/api/v1/user/'
   if(dept){
    api_url = '/api/v1/user/?dept='+dept
   }
   loader();
    $.ajax({
        url: api_url,
        type: 'GET',
        success: function (data) {
            hideloader();
            member_options = data;
            rosterMembers()
        },
        error: function (error) {
            hideloader();
        }
    });

}

$(window).on('load', async function () {
    $(".no-data").hide()
    hideloader();
    if (window.location.pathname == "/list/roster") {
        get_roster_data(1)
    }
    if (isNaN(parseInt(location.pathname.split('/')[2])) == false && location.pathname.split('/')[3] == "detail") {

        employeeOnLeave(split_date_format($("#from_date")[0].innerText), split_date_format($("#to_date")[0].innerText))
        loader();
        $.ajax({
            url: '/api/v1/roster/' + location.pathname.split('/')[2] + '/',
            type: 'get',
            dataType: 'json',
            success: function (data) {
                hideloader();
                mem_in_roster = data.members
            },
            error: function (error) {
                hideloader();
            }
        });
    }
    if (isNaN(parseInt(location.pathname.split('/')[2])) == false && location.pathname.split('/')[3] == "") {
        $(".clear-tc").hide()
       get_user_list()
        patch_form(parseInt(location.pathname.split('/')[2]))
    }
});

function rosterMembers() {
    $("#member_search_input").empty()
    if (member_options.length > 0){
        for (j = 0; j < member_options.length; j++) {
            var assign = ''
            if (empl_on_leave.length > 0) {
                for (i = 0; i < empl_on_leave.length; i++) {
                    if (member_options[j].id === empl_on_leave[i].employee){
                        assign = "disabled"
                    }
                }
            }
            selected = ''
            if (selected_member.length > 0) {
                for (i = 0; i < selected_member.length; i++) {
                    if (member_options[j].id === selected_member[i]){
                        selected = "selected"
                    }
                }
            }
            if (!assign){
                $('#member_search_input').append('<option value='+ member_options[j].id +' '+ assign +' '+ selected +'>'+ member_options[j].first_name +' '+ member_options[j].last_name +' ('+ member_options[j].email +')</option>')
            }
        }
    }
    else{
        $('#member_search_input').append(" <option disabled>No Members Found</option>")
    }
    $("#member_search_input").selectpicker("refresh");
}
$(function () {
    $('.selectpicker').selectpicker();
});

function create_roster() {
    if ($("#roster_form").valid() && check_date){
        var data = new FormData(document.getElementById('roster_form'));
        data.append('monday', monday)
        data.append('tuesday', tuesday)
        data.append('wednesday', wednesday)
        data.append('thursday', thursday)
        data.append('friday', friday)
        data.append('saturday', saturday)
        data.append('sunday', sunday)
        let members = []
        loader();
        $.ajax({
            url: '/api/v1/roster/',
            type: 'POST',
            data: data,
            processData: false,
            contentType: false,
            success: function (data) {
                hideloader();
                $("#roster_form")[0].reset();
                $("#emp_id").text(data.roster_no);
                $("#joning").text(data.members.length);
                $('#member_list').empty();
                $('#member_search_dropdown').empty();
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

function remove_member(id) {
    for (i = 0; i < member_list.length; i++) {
        if (member_list[i].id == id) {
            var index = member_list.indexOf(member_list[i]);
            member_list.splice(index, 1);
            document.getElementById(id).remove()
            break;
        }
    }
}

$("#to_date").change(function () {
    addMemberOptions();
    var startDate = document.getElementById("from_date").value;
    var endDate = document.getElementById("to_date").value;
    startDate = split_date_format(startDate)
    endDate = split_date_format(endDate)
    $("#error2").empty()

    if (!(Date.parse(startDate) < Date.parse(endDate))) {
        $("#error2").append("To date should be greater than From date.");
    }
    else{
        employeeOnLeave(startDate, endDate);
    }
    $("#to_date").valid()
});

function addMemberOptions(){
    if ($('#category').val() === null){
        $("#member_search_input").empty()
        $('#member_search_input').append("<option disabled>No Members Found</option>")
        $("#member_search_input").selectpicker("refresh");
    }
    else{
        get_user_list($('#category').val())
        rosterMembers()
    }
}

$("#from_date").change(function () {
    $('#member_search_dropdown').empty();
    $("#category").val('')
    addMemberOptions()
    var startDate = document.getElementById("from_date").value;
    getDate(startDate)
    var endDate = document.getElementById("to_date").value;
    startDate = split_date_format(startDate)
    endDate = split_date_format(endDate)
    if (!endDate == ''){
        $("#error2").empty()
        if (!(Date.parse(startDate) < Date.parse(endDate))) {
            $("#error2").append("To date should be greater than From date.");
        }
        else{
            employeeOnLeave(startDate, endDate);
        }
    }
    $("#from_date").valid()
});

function employeeOnLeave(startDate, endDate){
    loader();
    $.ajax({
        url: '/api/v1/data/leave/?start='+ startDate +'&end='+endDate,
        type : 'get',
        dataType:'json',
        success: function (data) {
            hideloader();
            empl_on_leave = data
            if (isNaN(parseInt(location.pathname.split('/')[2])) == false && location.pathname.split('/')[3] == "detail") {
                get_mem_roster()
            }
        },
        error: function (data) {
            hideloader();
        }
    });
}

function get_mem_roster(){
    loader();
    $.ajax({
        url: '/api/v1/roster/' + location.pathname.split('/')[2] + '/',
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

function patch_details(data){
    var classes = ''
    for (i = 0; i < data.members_detail.length; i++) {
        var img = "/static/assets/images/default-Image.jpg"
        if (data.members_detail[i].picture != ''){
            img = data.members_detail[i].picture
        }
        var classes = ''
        for (j = 0; j < empl_on_leave.length; j++) {
            if (data.members_detail[i].id == empl_on_leave[j]['employee']){
                classes = 'marked-blk'
            }
        }
        stri = '<div class="small-blk '+ classes +'"><div class="round-circle"><img src="'+ img +'" width="25"'+
             'height="25" alt="User-Profile"></div>'+data.members_detail[i].name+'</div>'
         $('.blk-container').append(stri)
    }
    if (!data.members_detail.length > 0) {
         $('#memmber').append(" NA")
    }
}

$('#to_time').change(function(){
 var startDate = $("#from_date").val();
    startDate = split_date_format(startDate)
    var endDate = $("#to_date").val();
    endDate = split_date_format(endDate)
    var timefrom = moment(startDate);
    temp = $('#from_time').val().split(":");
//    timefrom.setHours((parseInt(temp[0]) - 1 + 24) % 24);
    timefrom.set({ hour: (parseInt(temp[0])  + 24) % 24, minute:parseInt(temp[1])});

    var timeto = moment(endDate);
    temp = $('#to_time').val().split(":");
//    timeto.setHours((parseInt(temp[0]) - 1 + 24) % 24);
      timeto.set({ hour: (parseInt(temp[0])  + 24) % 24, minute:parseInt(temp[1])});
    check_date = true

    $("#error1").empty()
    if (!(timeto > timefrom)){
        $("#error1").append('To time should be greater than From time.');
        check_date = false
    }
    $('#to_time').valid()
    $('#from_time').valid()
});

$('#from_time').change(function(){
    $('#from_time').valid()
});

function getDate(date){
      date = split_date_format(date)
      var date1 = new Date(date);
      date1.setDate(date1.getDate() + 6);
      var dd = date1.getDate();
      var mm = date1.getMonth()+1;
      var yyyy = date1.getFullYear();

      if(dd<10) {
          dd = '0'+dd
      }
      if(mm<10) {
          mm = '0'+mm
      }
      today1 =   dd + '/' +  mm  + '/' + yyyy
      if (isNaN(parseInt(location.pathname.split('/')[2])) == false && location.pathname.split('/')[3] == "detail") {
        return today1
      }
      else{
        document.getElementById('to_date').value = today1;
      }
}

function toggle_workday(day) {
    switch (day) {
        case 'mon':
            monday = !monday
            if (monday) {
                document.getElementById(day).setAttribute('class', "days-blk bluebg")
            } else {
                document.getElementById(day).setAttribute('class', "days-blk")
            }
            break;
        case 'tue':
            tuesday = !tuesday
            if (tuesday) {
                document.getElementById(day).setAttribute('class', "days-blk bluebg")
            } else {
                document.getElementById(day).setAttribute('class', "days-blk")
            }
            break;
        case 'wed':
            wednesday = !wednesday
            if (wednesday) {
                document.getElementById(day).setAttribute('class', "days-blk bluebg")
            } else {
                document.getElementById(day).setAttribute('class', "days-blk")
            }
            break;
        case 'thu':
            thursday = !thursday
            if (thursday) {
                document.getElementById(day).setAttribute('class', "days-blk bluebg")
            } else {
                document.getElementById(day).setAttribute('class', "days-blk")
            }
            break;
        case 'fri':
            friday = !friday
            if (friday) {
                document.getElementById(day).setAttribute('class', "days-blk bluebg")
            } else {
                document.getElementById(day).setAttribute('class', "days-blk")
            }
            break;
        case 'sat':
            saturday = !saturday
            if (saturday) {
                document.getElementById(day).setAttribute('class', "days-blk bluebg")
            } else {
                document.getElementById(day).setAttribute('class', "days-blk")
            }
            break;
        case 'sun':
            sunday = !sunday
            if (sunday) {
                document.getElementById(day).setAttribute('class', "days-blk bluebg")
            } else {
                document.getElementById(day).setAttribute('class', "days-blk")
            }
            break;
        default:
            break;
    }
}

$(".previous-icon").click(function () { get_roster_data(roster_current_page - 1); });
$(".next-icon").click(function () { get_roster_data(roster_current_page + 1); });

function update_roster() {
if ($("#roster_form").valid() && check_date){
    var data = new FormData(document.getElementById('roster_form'));
    data.append('monday', monday)
    data.append('tuesday', tuesday)
    data.append('wednesday', wednesday)
    data.append('thursday', thursday)
    data.append('friday', friday)
    data.append('saturday', saturday)
    data.append('sunday', sunday)
    if (file_upload == false) {
        data.delete('terms_and_conditions')
    }
    member_list.forEach(member => {
        data.append('members', member.id)
    });
    loader();
    $.ajax({
        url: '/api/v1/roster/' + parseInt(location.pathname.split('/')[2]) + '/',
        type: 'put',
        data: data,
        cache: false,
        processData: false,
        contentType: false,
        success: function (data) {
            hideloader();
            window.setTimeout(function () {
                location.href = '/list/roster'
            }, 1000);
            $('.alert-success').show().delay(1500)
            $('#succ-msg').text('Roster edited successfully.')
        },
        error: function (data) {
            hideloader();
            var i = 0
            for (var key in data.responseJSON) {
                if (i == 0) {
                    $('.alert-danger').show().delay(1500)
                    $('#error_txt').text(data.responseJSON[key])
                }
                i = i + 1
            }
        }
    });
    }
}

function roaster_search(){
    var search = $('#member_search_input').val()
     var dept = $('#department').val()
    if (search != ''){
        var query = 'search='+search +'&&dept='+dept
    }
    else{
        var query = '&&dept='+dept
    }
    $.ajax({
        url : '/api/v1/roster/?'+query,
        type : 'get',
        dataType:'json',
        success : function(data) {
            pagination(data)
            roster_listtable(data)
        },
        error: function(data){
            hideloader();
        }
    });
}
$('#department').on('change', function(){
    roaster_search()
})

function get_roster_data(page) {
    loader();
    url = '/api/v1/roster/?page=' + page
    if ($('#department').val() != ''){
        url = '/api/v1/roster/?page=' + page+'&department='+$('#department').val()
    }
    $.ajax({
        url: url,
        type: 'get',
        dataType: 'json',
        success: function (data) {
            hideloader();
            roster_listtable(data)
            pagination(data)
        },
        error: function (error) {
            hideloader();
        }
    });
}
function pagination(data){
    roster_count_info = data['count']
    roster_current_page = data['current']
    roster_next = data['next']
    roster_prev = data['previous']
    roster_first_included = true
    roster_last_included = true
    roster_total_page = Math.ceil(data['count'] / 8)
    roster_pages = []

    for (var i = roster_current_page - 2; i <= roster_current_page + 2; i++) {
        if (i > 0 && i <= roster_total_page) {
            roster_pages.push(i);
        }
    }
    if (roster_current_page - 2 > 1) {
        roster_first_included = false
    }
    if (roster_current_page + 2 < roster_total_page) {
        roster_last_included = false
    }
    $(".next-icon-list").empty();
    for (var item of roster_pages) {
        $(".next-icon-list").append('<li><a class="element" href="javascript:get_roster_data(' + item + ');" id="' + item + '" title="">' + (item) + '</a></li>')
        if (roster_current_page == item) {
            $("#" + item)[0].parentNode.classList.add("active")
        }
    }
}
function patch_form(id) {
    loader();
    $.ajax({
        url: '/api/v1/roster/' + id + '/',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            hideloader();
            $("input[name='name']").val(data.name)
            $("input[name='roster_no']").val(data.roster_no)
            $("input[name='from_time']").val(data.from_time)
            $("input[name='to_time']").val(data.to_time)
            $("input[name='from_date']").val(new_date_format(data.from_date))
            $("input[name='to_date']").val(new_date_format(data.to_date))
            $("select[name='status']").val(data.status)
            $("select[name='department']").val(data.department)
            selected_member = data.members

            get_user_list(data.department)
            employeeOnLeave(data.from_date, data.to_date)


            if (data.terms_and_conditions != null){
                $("#term_file").append('<a href="'+ data.terms_and_conditions +'" target="_blank">'+data.doc_name+'</a>')
            }

            if (data.monday) {
                toggle_workday('mon')
            }
            if (data.tuesday) {
                toggle_workday('tue')
            }
            if (data.wednesday) {
                toggle_workday('wed')
            }
            if (data.thursday) {
                toggle_workday('thu')
            }
            if (data.friday) {
                toggle_workday('fri')
            }
            if (data.saturday) {
                toggle_workday('sat')
            }
            if (data.sunday) {
                toggle_workday('sun')
            }
            $("select[name='members']").val(data.members)
            $("#member_search_input").selectpicker("refresh");

        },
        error: function (error) {
            hideloader();
        }
    });
}



function handle_file_change() {
     $("#term_file").hide()
    file_upload = true
    if (document.getElementById('terms_and_conditions').files.length > 0) {
        $("#tc_file_list").empty()
        $("#tc_file_list").append(document.getElementById('terms_and_conditions').files[0].name)
        $("#tc_file_list").css("color", "#415c73")
    }
    else {
        $("#tc_file_list").empty()
        $("#tc_file_list").append("Attach Doc")
        $("#tc_file_list").css("color", "#97abbc")
    }
}

function roster_listtable(data) {
    $(".table-block").empty();
    stri = ''
    roster_item = document.createElement('tr')
    roster_item.setAttribute('class', 'table-block')
    result_len = (data.results.length)
    $(".no-data").empty()

    if (result_len != 0){
        for (i = 0; i < result_len; i++) {
            leavedata(data.results[i].from_date, data.results[i].to_date, data.results[i].members, data.results[i].id)
            stri = '<tr class="table-block '+ data.results[i].id +'">'
                +'<td><div>'+ data.results[i].name + '</div></td><td>'+ data.results[i].roster_no + '</td> <td><div>'+ data.results[i].dept_name + '</div></td><td><div>'
                + get_date(data.results[i].from_date) +' To '+ get_date(data.results[i].to_date) +'</div></td>'
                + '<td>'
                + convert_time(data.results[i].from_time) +' To '+ convert_time(data.results[i].to_time) +'</td>'
                + '<td>'
            if (data.results[i].monday == false) {
                stri = stri + '<a href="javascript:void(0);" title="" class="box">Mon</a>'
            }
            if (data.results[i].tuesday == false) {
                stri = stri + '<a href="javascript:void(0);" title="" class="box">Tue</a>'
            }
            if (data.results[i].wednesday == false) {
                stri = stri + '<a href="javascript:void(0);" title="" class="box">Wed</a>'
            }
            if (data.results[i].thursday == false) {
                stri = stri + '<a href="javascript:void(0);" title="" class="box">Thu</a>'
            }
            if (data.results[i].friday == false) {
                stri = stri + '<a href="javascript:void(0);" title="" class="box">Fri</a>'
            }
            if (data.results[i].saturday == false) {
                stri = stri + '<a href="javascript:void(0);" title="" class="box">Sat</a>'
            }
            if (data.results[i].sunday == false) {
                stri = stri + '<a href="javascript:void(0);" title="" class="box">Sun</a>'
            }
            stri = stri
                + '</td><td><span class="cus-badge '+ get_class(data.results[i].status) +'">'+ status(data.results[i].status)+'</span>'+
                '</td><td class="text-center">'+ data.results[i].members.length+ '</td><td class="actions"><a href="/roster/'+ data.results[i].id+'/detail/"'+
                'onclick="myFunction()" title="View" class="icon-blk green-block"><i class="fas fa-eye"></i></a><a href="/roster/'+ data.results[i].id+ '/" title="Edit"'+
                 'class="blue-block icon-blk"><i class="fas fa-pen"></i></a></td></tr>'
            document.getElementById('roster_table').innerHTML = document.getElementById('roster_table').innerHTML + stri;
        }
    }
    else{
        $(".no-data").show()
        $(".no-data").append('<div class="center-txt">No Record Found.</div>')
    }
}

function get_date(date){
    return  moment(date).format('DD/MM/YYYY');

}
function split_date_format(date){
    return date.split('/')[2] + "-" + date.split('/')[1] + "-" + date.split('/')[0]
}
function query_date_format(date){
    var myDate = new Date(date);
    return myDate.getFullYear() + "-" + (myDate.getMonth() + 1) + "-" + myDate.getDate()

}
function new_date_format(date){
    var myDate = new Date(date);
    return  myDate.getDate() + "/" + (myDate.getMonth() + 1) + "/" + myDate.getFullYear()

}

function leavedata(start, end, member, id){
    loader();
    $.ajax({
            url: '/api/v1/data/leave/?start='+ start +'&end='+end,
            type : 'get',
            dataType:'json',
            success: function (data) {
                hideloader();
                catchLeave(data, member, id)
            },
            error: function (data) {
                hideloader();
            }
        });
}
function catchLeave(data, member, id){
    for(i = 0; i < member.length; i++){
        for(j = 0; j < data.length; j++){
            if (member[i] == data[j]['employee']){
                $("."+ id).css("color", "#e66c55")
            }
        }
    }
}
function get_class(status){
    if (status == "1"){
        return "green-badge"
    }
    else if(status == "2"){
        return 'red-badge'
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
$.validator.addMethod('positiveNumber',function (value) {
        return Number(value) > 0;
    }, 'Enter a positive number.');

$("#roster_form").validate({
    errorPlacement: function errorPlacement(error, element) {
        element.after(error);
    },
    errorClass: 'custom-error',
    rules: {
        name: {
            required: true,
            minlength: 1,
            maxlength: 30
        },
        roster_no: {
            required: true,
            positiveNumber: true,
             remote: {
                url: "/api/v1/roster/check_roster/",
                type: "get",
                data: {
                    'department': function(){
                        return $('#category').val();
                    },
                    'id' : function(){
                    return parseInt(location.pathname.split('/')[2]);
                    }
                }
                }
        },
        from_time: {
            required: true,
        },
        to_time: {
            required: true,
        },
        from_date: {
            required: true,
        },
        to_date: {
            required: true,
        },
        status: {
            required: true,
        },
        department: {
            required: true,
//            remote: {
//                url: "/api/v1/roster/check_roster/",
//                type: "get",
//                data: {
//                    'roster_no': function(){
//                        return $('#roster_number').val();
//                    },
//                    'id' : function(){
//                    return parseInt(location.pathname.split('/')[2]);
//                    }
//                }
//                }
        },
    },
    messages: {
        name: {
            required: 'Please enter the Roster Name. ',
            minlength: 'Roster Name have atleast 1 characters.',
            maxlength: 'Roster Name should be less than equal to 30 characters.'
        },
        roster_no: {
            required: 'Please enter the Roster No.',
            positiveNumber: 'Please enter the Positive Numbers only.',
            remote : 'Roster with this number already exists.',
        },
        from_time: {
            required: 'Please select the from field.',
        },
        to_time: {
            required: 'Please select the to field.',
        },
        from_date: {
            required: 'Please select the from field.',
        },
        to_date: {
            required: 'Please select the to field.',
        },
        status: {
            required: "Please select the status field.",
        },
        department: {
            required: 'Please select a department.',
        },
    },
});

function export_data(email=false, file_type='pdf') {
    if ($("#department").val() == ''){
        var url ='/api/v1/export/rosters?file_type='+file_type
    }
    else{
        var url ='/api/v1/export/rosters?file_type='+file_type+'&department='+$("#department").val()
    }
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

$('#roster_number, #roster_no').keypress(function() {
    var charCode = (window.event.which) ? window.event.which : window.event.keyCode;
    if (charCode > 31 && (charCode < 48 || charCode > 57)) {
        return false;
    }
    return true;
        });
$('#category').on('change', function(){

    if (window.location.pathname == "/add/roster") {
        $('#roster_number').valid()
    }
    else{
        $('#roster_no').valid()
    }
    member_list = []
    $('#member_list').empty();
    get_user_list($(this).val())
});

function loader(){
    $('.dynamic-loader').show()
    $('.overlay').show()
}
function hideloader(){
    $('.dynamic-loader').hide()
    $('.overlay').hide()
}