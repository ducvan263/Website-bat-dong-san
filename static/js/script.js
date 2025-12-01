function showPass() {
    var x = document.getElementById("pass");
    if (x.type === "password") {
        x.type = "text";
    } else {
        x.type = "password";
    }
}

function showComPass() {
    var x = document.getElementById("comPass");
    if (x.type === "password") {
        x.type = "text";
    } else {
        x.type = "password";
    }
}

var myIndex = 0;
showImg();

// function showImg() {
//     var i;
//     var x = document.getElementsByClassName("mySlider");
//     for (i = 0; i < x.length; i++) {
//         x[i].style.display = "none";
//     }
//     myIndex++;
//     if (myIndex > x.length) { myIndex = 1 }
//     x[myIndex - 1].style.display = "block";
//     setTimeout(showImg, 2000);
//     console.log(2);
//     console.log(x.length);

// }

function showInput() {
    var checkBox = document.getElementById("squaredcheck4");
    if (checkBox.checked == true) {
        document.getElementById('contact-input-diff').style.display = "block";
    } else {
        document.getElementById('contact-input-diff').style.display = "none";
    }
}

function togglecheckboxes(cn) {
    var cbarray = document.getElementsByName(cn);
    var checkBox = document.getElementById("squaredcheck4");
    for (var i = 0; i < cbarray.length; i++) {
        if (cbarray[i].checked === true) {
            cbarray[i].checked = false;
        }
        if (checkBox.checked == true) {
            cbarray[i].disabled = true;
        } else {
            cbarray[i].disabled = false;
        }

    }
}