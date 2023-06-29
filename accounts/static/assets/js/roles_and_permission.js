var department = ''

$(window).on('load', function(){
    hideloader();
    roles_table()
});
function submit_form(){
    if ($("#roles_form").valid()){
        var data = $("#roles_form")[0]
        var form_data = new FormData(data)
//        loader();
        $.ajax({
            url : '/api/v1/roles/permission/',
            type : 'POST',
            data : form_data,
            cache: false,
            processData: false,
            contentType: false,

            success : function(data) {
                hideloader();
                $('.alert-success').show().delay(1500)
                window.setTimeout(function(){
                    location.href = '/user/roles'
                }, 1000);
                $('#succ-msg').text('Roles and permission added successfully.')
            },
            error: function(data) {
                hideloader();
                 var i = 0
               for (var key in data.responseJSON) {
                   if (i ==0){
                    $('.alert-danger').show().delay(1000)
                    $('#error_txt').text(key + ' '+ data.responseJSON[key][0])
                   }
                   i = i +1

                }
            }
        });
    }
}
$('#department').on('change', function(){
    department = $(this).val()
    roles_table()
})
function roles_table(){
    urls = '/api/v1/roles/permission/'
    if (department){
        urls = '/api/v1/roles/permission/?department='+department
    }
    loader();
    $(".table-data").empty()
    $.ajax({
        url : urls,
        type : 'get',
        dataType:'json',
        success : function(data) {
            hideloader();
            $('#no-data').empty();
            console.log(data)
            if (data.length > 0){
                for (i=data.length-1;i>=0;i--){
                    stri = '<tr class="top-border table-data"><td class="border-rt">'+data[i].designation_name+'</td><td class="check-blk text-center">'+
                           '<label class="custum-container"><input type="checkbox"  class="lost" id="main_'+data[i].id+'" onclick="handleClick(this, '+data[i].id+');"><span class="checkmark"></span></label></td>'+
                           '<td class="check-blk text-center"><label class="custum-container"><input type="checkbox" id="bus_'+data[i].id+'" onclick="handleClick(this, '+data[i].id+');"><span class="checkmark"></span></label></td>'+
                           '<td class="check-blk text-center"><label class="custum-container"><input type="checkbox" id="repair_'+data[i].id+'" onclick="handleClick(this, '+data[i].id+');"><span class="checkmark"></span></label></td>'+
                           '<td class="check-blk text-center"><label class="custum-container"><input type="checkbox" id="man_'+data[i].id+'" onclick="handleClick(this, '+data[i].id+');"><span class="checkmark"></span></label></td>'+
                           '<td class="check-blk text-center"><label class="custum-container"><input type="checkbox" id="work_'+data[i].id+'" onclick="handleClick(this, '+data[i].id+');"><span class="checkmark"></span></label></td>'+
                           '<td class="check-blk text-center"><label class="custum-container"><input type="checkbox" id="service_'+data[i].id+'" onclick="handleClick(this, '+data[i].id+');"><span class="checkmark"></span></label></td>'+
                           '<td class="check-blk text-center"><label class="custum-container"><input type="checkbox" id="user_'+data[i].id+'" onclick="handleClick(this, '+data[i].id+');"><span class="checkmark"></span></label></td>'+
                           '<td class="check-blk text-center"><label class="custum-container"><input type="checkbox" id="busedit_'+data[i].id+'" onclick="handleClick(this, '+data[i].id+');"><span class="checkmark"></span></label></td>'+
                           '<td class="check-blk text-center"><label class="custum-container"><input type="checkbox" id="order_'+data[i].id+'" onclick="handleClick(this, '+data[i].id+');"><span class="checkmark"></span></label></td>'+
                           '<td class="check-blk text-center"><label class="custum-container"><input type="checkbox" id="email_'+data[i].id+'" onclick="handleClick(this, '+data[i].id+');"><span class="checkmark"></span></label></td>'+
                           '</tr>'

                    $('#roles-body').append(stri)

                    $('#main_'+data[i].id+'').prop('checked', data[i].main_dashboard);
                    $('#bus_'+data[i].id+'').prop('checked', data[i].bus_management);
                    $('#repair_'+data[i].id+'').prop('checked', data[i].repair_request);
                    $('#man_'+data[i].id+'').prop('checked', data[i].man_management);
                    $('#work_'+data[i].id+'').prop('checked', data[i].work_management);
                    $('#service_'+data[i].id+'').prop('checked', data[i].service_request);
                    $('#user_'+data[i].id+'').prop('checked', data[i].user_admin_management);
                    $('#busedit_'+data[i].id+'').prop('checked', data[i].bus_edit);
                    $('#order_'+data[i].id+'').prop('checked', data[i].work_show);
                    $('#email_'+data[i].id+'').prop('checked', data[i].email_rr);
                }
            }
            else{
                stri = '<h3 class="record center-txt">No Designation Found</h3>'
                $('#no-data').append(stri)
            }

        },
        error: function(error) {
            hideloader();
        }
    });
}
function handleClick(id,a){
    if ($(id).attr('id').split('_')[0] == 'main'){
        data = {"main_dashboard": $(id)[0].checked}
    }if ($(id).attr('id').split('_')[0] == 'bus'){
        data = {"bus_management": $(id)[0].checked}
    }if ($(id).attr('id').split('_')[0] == 'repair'){
        data = {"repair_request": $(id)[0].checked}
    }if ($(id).attr('id').split('_')[0] == 'man'){
        data = {"man_management": $(id)[0].checked}
    }if ($(id).attr('id').split('_')[0] == 'work'){
        data = {"work_management": $(id)[0].checked}
    }if ($(id).attr('id').split('_')[0] == 'service'){
        data = {"service_request": $(id)[0].checked}
    }if ($(id).attr('id').split('_')[0] == 'user'){
        data = {"user_admin_management": $(id)[0].checked}
    }if ($(id).attr('id').split('_')[0] == 'order'){
        data = {"work_show": $(id)[0].checked}
    }if ($(id).attr('id').split('_')[0] == 'busedit'){
        data = {"bus_edit": $(id)[0].checked}
    }if ($(id).attr('id').split('_')[0] == 'email'){
        data = {"email_rr": $(id)[0].checked}
        console.log(data)
    }
    $.ajax({
            url : '/api/v1/roles/permission/'+a+'/',
            type : 'put',
            data : data,
            dataType:'json',
            success : function(data) {

            },
            error: function(data) {
                }
        });
}

$("#bus-table").on("change", function(){
    $.ajax({
        url : '/api/v1/registration/modules/',
        type : 'put',
        data : {'all_buses': $(this)[0].checked},
        dataType:'json',
        success : function(data) {

        },
        error: function(data) {
            }
    });
})
$("#work-order").on("change", function(){
    $.ajax({
        url : '/api/v1/registration/modules/',
        type : 'put',
        data : {'total_wo': $(this)[0].checked},
        dataType:'json',
        success : function(data) {

        },
        error: function(data) {
            }
    });
})
$("#bus-analytics").on("change", function(){
    $.ajax({
        url : '/api/v1/registration/modules/',
        type : 'put',
        data : {'bus_analytics': $(this)[0].checked},
        dataType:'json',
        success : function(data) {

        },
        error: function(data) {
            }
    });
})
$("#bus-calendar").on("change", function(){
    $.ajax({
        url : '/api/v1/registration/modules/',
        type : 'put',
        data : {'bus_calendar': $(this)[0].checked},
        dataType:'json',
        success : function(data) {

        },
        error: function(data) {
            }
    });
})

function loader(){
    $('.dynamic-loader').show()
    $('.overlay').show()
}
function hideloader(){
    $('.dynamic-loader').hide()
    $('.overlay').hide()
}