var file_upload = true


$(window).on('load', function(){
    hideloader();

});

function submit_image(){
    if ($("#image_form").valid() && file_upload){
        var data = $("#image_form")[0]
        var form_data = new FormData(data)
        loader();

        $.ajax({
            url : '/api/v1/upload/image/update_profile/',
            type : 'put',
            data : form_data,
//            dataType:'json',
            cache: false,
            processData: false,
            contentType: false,
            success : function(data) {
                hideloader();
                window.setTimeout(function(){
                    location.href = '/user/accounts'
                }, 1000);
                 $('.alert-success').show().delay(1500)
                 $('#imageModal').modal('hide');
                $('#succ-msg').text('Profile Picture uploaded successfully.')
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


}
$("#profile_picture").on('change', function(){
    validate_file(this)
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
})
function loader(){
    $('.dynamic-loader').show()
    $('.overlay').show()
}
function hideloader(){
    $('.dynamic-loader').hide()
    $('.overlay').hide()
}

function validate_file(file){
    const validImageTypes = ['image/jpg', 'image/jpeg', 'image/png'];
    var name=$(file).attr('id')
        console.log(file.files[0].name)
        if (!validImageTypes.includes(file.files[0].type)){
            console.log(111111111111)
            console.log(name)
            $("#"+name+"1").text("Please select Only .jpg, .png and .jpeg format.")
             file_upload = false
            }
        else{
            console.log(name)
            file_upload = true
            var reader = new FileReader();
            console.log(reader)
            reader.onload = function(e) {
                console.log(e.target.result)
                $('#profile').attr('src', e.target.result);
            }
            $("#"+name+"1").text('')
        }
}
function submit_edit(){
    if ($("#add_employee_form").valid()){
        var data = $("#add_employee_form")[0]
        var form_data = new FormData(data)
        loader();
        $.ajax({
            url : '/api/v1/upload/image/edit/',
            type : 'put',
            data : form_data,
//            dataType:'json',
            cache: false,
            processData: false,
            contentType: false,
            success : function(data) {
                window.setTimeout(function(){
                    location.href = '/user/accounts'
                }, 1000);
                $('#editModal').modal('hide');
                hideloader();
                 $('.alert-success').show().delay(1500)
                $('#succ-msg').text('Profile has been edited successfully.')
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

}
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
        contact: {
            numbersonly: false,
            minlength : 12,
            maxlength: 12
        }
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

        contact: {
            numbersonly: "Please enter the digits only.",
            minlength: "Contact should be at least 10 digits.",
            maxlength: 'Contact should be less than equal to 10 digits.'
        }
    },
});

$("#image_form").validate({
    errorPlacement: function errorPlacement(error, element) {
        document.getElementById('profile_picture1').append(error[0]);
    },
    errorClass: 'custom-error',
    rules: {
        profile_picture: {
            required: true,
        },
    },
    messages: {
        profile_picture: {
            required: 'Please select image. ',
        }
}});