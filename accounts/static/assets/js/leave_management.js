var bus_count_info
var bus_current_page = 0
var bus_next = null
var bus_prev = null
var bus_first_included=true
var bus_last_included=true
var bus_total_page = 0
var bus_pages = []
var file_upload = true
var key = ''
$(window).on('load', function(){
    hideloader();
    if (window.location.pathname == "/leave/listing"){
        get_leave_data(1, 'pending')
    }
    a = parseInt(location.pathname.split('/')[2])
    let b =location.pathname.split('/')[3]
    if (isNaN(a) == false){
        get_leave_detail(a, b)
   }
});

function get_date(date){
    return  moment(date).format('DD/MM/YYYY');

}

$(".previous-icon").click(function(){ get_leave_data(bus_current_page - 1, key); });
$(".next-icon").click(function(){ get_leave_data(bus_current_page + 1, key); });

$('#file').on ('change', function () {
    $(".form-btn-sec").show()

    if (this.files.length > 0) {
        $("#bus_photos1").empty()
            var extension = this.files[0].name.substr( (this.files[0].name.lastIndexOf('.') +1) );
     extension = extension.toLowerCase()

        if (extension != 'csv'){

            $("#bus_photos1").append("Please select Only .csv format file.")
            file_upload = false
        }
        else{
            file_upload = true
        }
        $(".proof").empty()
        $(".proof").append(this.files[0].name)
        $(".proof").css("color", "#415c73")
    }
    else {
        $(".proof").empty();
        $(".proof").append("Select File")
        $(".proof").css("color", "#97abbc")
    }
})
$("#pending").on('click', function(){
    get_leave_data(1, 'pending')
});
$("#approved").on('click', function(){
    get_leave_data(1, 'approved')
});
$("#rejected").on('click', function(){
    get_leave_data(1, 'rejected')
});
$("#all").on('click', function(){
    get_leave_data(1, 'all')
});

function get_leave_data(page, args= null){
    key = args
    activeclass()
    loader();
    $.ajax({
        url : '/api/v1/leaves/uploadcsv/?page='+ page +'&'+ key +'=1',
        type : 'get',
        dataType:'json',
        success : function(data) {
            hideloader();
            pagination(data)
            leave_table(data)
            if (data.count == 0){
                $(".table-block").empty();
                $(".no-data").show();
            }
        else{
            $(".no-data").hide();
        }
        },
        error: function(error) {
            hideloader();
        }
    });
}
function pagination(data){
    bus_count_info = data['count']
    bus_current_page = data['current']
    bus_next = data['next']
    bus_prev = data['previous']
    bus_first_included = true
    bus_last_included = true
    bus_total_page = Math.ceil(data['count']/8)
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
        $(".next-icon-list").append(`<li><a class="element" href="javascript:get_leave_data(${item}, '${key}');" id="${item}" title="">${item}</a></li>`)
        if (bus_current_page == item){
            $("#"+item)[0].parentNode.classList.add("active")
        }
    }
}

function activeclass(){
   if (key === 'all'){
        var element = document.getElementById("pending");
        element.classList.remove("filter-active");
        var element = document.getElementById("approved");
        element.classList.remove("filter-active");
        var element = document.getElementById("rejected");
        element.classList.remove("filter-active");
        var element = document.getElementById("all");
        element.classList.add("filter-active");
   }
   if (key === 'pending'){
        var element = document.getElementById("pending");
        element.classList.add("filter-active");
        var element = document.getElementById("approved");
        element.classList.remove("filter-active");
        var element = document.getElementById("rejected");
        element.classList.remove("filter-active");
        var element = document.getElementById("all");
        element.classList.remove("filter-active");
   }
   if (key === 'approved'){
        var element = document.getElementById("pending");
        element.classList.remove("filter-active");
        var element = document.getElementById("approved");
        element.classList.add("filter-active");
        var element = document.getElementById("rejected");
        element.classList.remove("filter-active");
        var element = document.getElementById("all");
        element.classList.remove("filter-active");
   }
   if (key === 'rejected'){
        var element = document.getElementById("pending");
        element.classList.remove("filter-active");
        var element = document.getElementById("approved");
        element.classList.remove("filter-active");
        var element = document.getElementById("rejected");
        element.classList.add("filter-active");
        var element = document.getElementById("all");
        element.classList.remove("filter-active");
   }
}
function get_pending_leave_data(page){
    var element = document.getElementById("all");
    element.classList.remove("filter-active");
    var element = document.getElementById("approved");
    element.classList.remove("filter-active");
    var element = document.getElementById("rejected");
    element.classList.remove("filter-active");
    var element = document.getElementById("pending");
    element.classList.add("filter-active");
    loader();
    $.ajax({
        url : '/api/v1/leaves/uploadcsv/?page='+page+"&pending=1",
        type : 'get',
        dataType:'json',
        success : function(data) {
            hideloader();
            if (data.count == 0){
                $(".table-block").empty();
                $(".no-data").show();
            }
        else{
            $(".no-data").hide();
            leave_table(data)
            bus_count_info = data['count']
            bus_current_page = data['current']
            bus_next = data['next']
            bus_prev = data['previous']
            bus_first_included = true
            bus_last_included = true
            bus_total_page = Math.ceil(data['count']/8)
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
                $(".next-icon-list").append('<li><a class="element" href="javascript:get_pending_leave_data('+item+');" id="'+item+'" title="">'+(item)+'</a></li>')
                if (bus_current_page == item){
                    $("#"+item)[0].parentNode.classList.add("active")
                }
            }

        }
        },
        error: function(error) {
            hideloader();
        }
    });
}

function get_approved_leave_data(page){
    var element = document.getElementById("pending");
    element.classList.remove("filter-active");
    var element = document.getElementById("all");
    element.classList.remove("filter-active");
    var element = document.getElementById("rejected");
    element.classList.remove("filter-active");
    var element = document.getElementById("approved");
    element.classList.add("filter-active");
    loader();
    $.ajax({
        url : '/api/v1/leaves/uploadcsv/?page='+page+"&approved=1",
        type : 'get',
        dataType:'json',
        success : function(data) {
            hideloader();
            if (data.count == 0){
                $(".no-data").show();
                $(".table-block").empty();
            }
        else{
            $(".no-data").hide();
            leave_table(data)
            bus_count_info = data['count']
            bus_current_page = data['current']
            bus_next = data['next']
            bus_prev = data['previous']
            bus_first_included = true
            bus_last_included = true
            bus_total_page = Math.ceil(data['count']/8)
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
                $(".next-icon-list").append('<li><a class="element" href="javascript:get_approved_leave_data('+item+');" id="'+item+'" title="">'+(item)+'</a></li>')
                if (bus_current_page == item){
                    $("#"+item)[0].parentNode.classList.add("active")
                }
            }

        }
        },
        error: function(error) {
            hideloader();
        }
    });
}

function get_rejected_leave_data(page){
    var element = document.getElementById("pending");
    element.classList.remove("filter-active");
    var element = document.getElementById("approved");
    element.classList.remove("filter-active");
    var element = document.getElementById("all");
    element.classList.remove("filter-active");
    var element = document.getElementById("rejected");
    element.classList.add("filter-active");
    loader();
    $.ajax({
        url : '/api/v1/leaves/uploadcsv/?page='+page+"&rejected=1",
        type : 'get',
        dataType:'json',
        success : function(data) {
            hideloader();
            if (data.count == 0){
                $(".no-data").show();
                $(".table-block").empty();
            }
        else{
            $(".no-data").hide();
            leave_table(data)
            bus_count_info = data['count']
            bus_current_page = data['current']
            bus_next = data['next']
            bus_prev = data['previous']
            bus_first_included = true
            bus_last_included = true
            bus_total_page = Math.ceil(data['count']/8)
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
                $(".next-icon-list").append('<li><a class="element" href="javascript:get_rejected_leave_data('+item+');" id="'+item+'" title="">'+(item)+'</a></li>')
                if (bus_current_page == item){
                    $("#"+item)[0].parentNode.classList.add("active")
                }
            }

        }
        },
        error: function(error) {
            hideloader();
        }
    });
}


function get_class(status){
    if (status == "approved"){
        return "green-badge"
    }
    else if(status == "rejected"){
        return 'red-badge'
    }
    else{
        return 'yellow-badge '
    }

}
function leave_table(data){

    $(".table-block").empty();
    stri = ''
    result_len= (data.results.length)
    rejected = "rejected"
    approved = "approved"
    for (i=result_len-1;i>=0;i--){
        stri1 = ''
        if (data.results[i].status == 'pending'){
            stri1 = '<td class="actions"><a href="javascript:void(0);" data-toggle="modal" onclick="addID('+ data.results[i].id +')" data-target="#myModal" title="Decline" class="icon-blk green-block">'+
                '<i class="fas fa-times"></i></a><a href="javascript:void(0);" onclick="approve('+ data.results[i].id +','+ approved +')" title="Approve" class="blue-block icon-blk">'+
                '<i class="fas fa-check"></i></a></td>'
        }
        if (data.results[i].status == 'approved'){
            stri1 = '<td class="actions"><button class="red-btn" id="'+ data.results[i].id +'" type="button" data-toggle="modal" onclick="addID(this.id)" data-target="#myModal">Cancel</button>'+
                '</td>'
        }
        stri='<tr class="table-block">'+
            '<td>'+ data.results[i].name +'</td><td><a href="/detail/'+ data.results[i].id +'/leave">'+ data.results[i].employee_id +'</a></td><td>'+ data.results[i].email +'</td>'+
            '<td>'+ data.results[i].description +'</td><td>'+ get_date(data.results[i].from_date) +' To '+ get_date(data.results[i].to_date) +'</td><td><span class="cus-badge '+get_class(data.results[i].status)+'">'+ data.results[i].status +'</span>'+
            '' +stri1 +'</td></tr>'
            $(".header-row").after(stri);

    }
}
function addID(id){
    $('.unique').eq(0).attr('id', id);
}

$(".leave").hide()
function upload_csv(){
    if ($("#upload_leave").valid() && file_upload) {
        var data = $("#upload_leave")[0]
        var form_data = new FormData(data)
        loader();
        $.ajax({
            url: '/api/v1/leaves/uploadcsv/',
            type : 'POST',
            data : form_data,
            cache: false,
            processData: false,
            contentType: false,
            success: function (data) {
                hideloader();
                document.getElementById("catch").style.display = 'block'
                document.getElementById("catch1").style.display = 'block'
                document.getElementById("catch3").style.display = 'block'
                leaves_stats(data)
                $(".form-btn-sec").hide()

            },
            error: function (data) {
                hideloader()
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

function leaves_stats(data){
    $(".leave").show()
    $(".error").empty()
    $(".upserts").empty()
    $(".summaries").empty()
    stri = '<li>No error</li>'
    stri2 = '<li>No Upserts</li>'
    if (data.errors.length > 0){
        for (let [key, value] of Object.entries(data.errors)){
            for (let [i, j] of Object.entries(value)){
                stri='<ul><li>Line '+ i +': '+ j[0] +' </li></ul>'
                $(".error").append(stri)
            }
        }
    }
    else{$(".error").append(stri)}
    if (data.summaries.length > 0){
        for (i=0;i<data.summaries.length;i++){
            stri1='<ul><li>'+ data.summaries[i] +' </li></ul>'
            $(".summaries").append(stri1)
        }
    }
    if (data.upserts.length > 0){
       for (i=0;i<data.upserts.length;i++){
            stri2 = '<ul ><li>'+ data.upserts[i]+'</li></ul>'
            $(".upserts").append(stri2)
        }
    }
    else{$(".upserts").append(stri2)}
}


function cancel_leave(id, status){


    if ($("#cancel_form").valid()){
        approve(id, status)
    }
    else{
        $('#comments-error').show()
        $('#comments-error').text('Please enter comments.')
    }
}

function approve(id, status){
    var comment = $('#comment')[0].value
    loader();
    $.ajax({
    url : '/api/v1/leaves/uploadcsv/'+id+'/',
    type : 'put',
    data : {'status': status, 'comments': comment},
    dataType:'json',
    success : function(data) {
        hideloader();
        if (window.location.pathname == "/leave/listing"){
            get_leave_data(bus_current_page, 'pending')

            $('#myModal').modal('hide')
            $("#cancel_form")[0].reset()
        }
        else{
            hideloader();
            location.reload();
        }
    },
    error: function(data) {
        hideloader();
        var i = 0
       for (var key in data.responseJSON) {
           if (i ==0){
            $('.alert-danger').show().delay(1500)
            $('#error_txt').text(key + ' '+ data.responseJSON[key][0])
           }
           i = i +1

        }
    }
    });
}

function get_leave_detail(id){
    loader();
    $.ajax({
        url : '/api/v1/leaves/uploadcsv/'+id+'/',
        type : 'get',
        dataType:'json',
        success : function(data) {
            hideloader();
            patch_detail(data)
        },
         error: function(error) {
             hideloader();
        }
    });
}


function patch_detail(data){
    $(".form-btn-sec").show()
    $("#name").html(data.name)
     $("#empId").text(data.employee_id)
     $("#production_year").text((data.make_year != '' && data.make_year != null) ? data.make_year :  'NA')
     $("#email").text(data.email)
     $("#contact").text(((data.contact != '' && data.contact != null) ? data.contact : 'NA' ))
     $("#department").text(data.department)
     $("#designation").text(data.designation)
     $("#leave_status").text(titleCase(data.status))
     $("#leave_date").text(data.from_date +' To '+ data.to_date)
     $("#description").text((data.description != '' && data.description != null) ? data.description :  'NA')

    rejected = "rejected"
    addID(data.id,rejected)
    approved = "approved"
    $('#decline_button').attr("onclick", 'approve('+data.id+','+rejected+')')
    $('#approve_button').attr("onclick", 'approve('+data.id+','+approved+')')
    $('#cancel_button').attr("onclick", 'approve('+data.id+','+rejected+')')
    if (data.status != "pending"){
        $(".form-btn-sec").hide()
    }
    if (data.status == "approved"){
        $(".cancl-btn").show()
    }
    else{
        $(".cancl-btn").hide()
     }

    if (data.profile_pic != ''  && data.profile_pic != null){
     $('.img-fluid').attr('src', data.profile_pic);
    }

}

function export_data(email=false, file_type='pdf') {
    var url ='/api/v1/export/leaves?file_type='+file_type
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

$("#upload_leave").validate({
    errorPlacement: function errorPlacement(error, element) {
        document.getElementById('bus_photos1').append(error[0]);
    },
    errorClass: 'custom-error',
    rules: {
        file: {
            required: true,
        },
    },
    messages: {
        file: {
            required: 'Please select file. ',
        }
}});

function titleCase(str) {
   var splitStr = str.toLowerCase().split(' ');
   for (var i = 0; i < splitStr.length; i++) {
       // You do not need to check if i is larger than splitStr length, as your for does that for you
       // Assign it back to the array
       splitStr[i] = splitStr[i].charAt(0).toUpperCase() + splitStr[i].substring(1);
   }
   // Directly return the joined string
   return splitStr.join(' ');
}
$(function () {
 $("#cancel_form").validate({


    errorPlacement: function errorPlacement(error, element) {
         element.after(error);
    },
    errorClass: 'custom-error',
    rules: {
        comments:{
            required: true,
        },
        comments:'required'
    },
    messages: {
        comments: {
            required: 'Please select Only .jpg, .png and .jpeg format are allowed.'
        },
         comments:'Please enter comments.'
    },

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