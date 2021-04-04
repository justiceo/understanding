<!-- CSS only -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-eOJMYsd53ii+scO/bJGFsiCZc+5NDVN2yr8+0RDqr0Ql0h+rP48ckxlpbzKgwra6" crossorigin="anonymous">
<!-- JavaScript Bundle with Popper -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/js/bootstrap.bundle.min.js" integrity="sha384-JEW9xMcG8R+pH31jmWH6WWP0WintQrMb4s7ZOdauHnUtxwoG2vI5DkLtS3qm9Ekf" crossorigin="anonymous"></script>
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/underscore.js/1.4.1/underscore-min.js" integrity="sha512-xHPfYya0Ac9NYcp0d6YKVnP/n7dcRGiQCsGKC+BMpziXwgg/6VogplMOS+nqUXQIPmtuGwZ25fAcSgtjBxBVfg==" crossorigin="anonymous"></script>

<div id="preloader"  style="display: none;">
    <div id="loader"></div>
</div>
<div class="body">
    <div class="d-flex justify-content-center mt-5">
        <button type="button" class="btn btn-primary btn-lg" id="generate-data">Generate Data</button>
    </div>
    <div class="container mt-5">
        <h2>Results:</h2>
        <div class="result-box" id="result-box">
        <div>
    </div>
</div>



<style>
#preloader {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
}
#loader {
    display: block;
    position: relative;
    left: 50%;
    top: 40%;
    width: 150px;
    height: 150px;
    margin: -75px 0 0 -75px;
    border-radius: 50%;
    border: 3px solid transparent;
    border-top-color: #9370DB;
    -webkit-animation: spin 2s linear infinite;
    animation: spin 2s linear infinite;
}
#loader:before {
    content: "";
    position: absolute;
    top: 5px;
    left: 5px;
    right: 5px;
    bottom: 5px;
    border-radius: 50%;
    border: 3px solid transparent;
    border-top-color: #BA55D3;
    -webkit-animation: spin 3s linear infinite;
    animation: spin 3s linear infinite;
}
#loader:after {
    content: "";
    position: absolute;
    top: 15px;
    left: 15px;
    right: 15px;
    bottom: 15px;
    border-radius: 50%;
    border: 3px solid transparent;
    border-top-color: #FF00FF;
    -webkit-animation: spin 1.5s linear infinite;
    animation: spin 1.5s linear infinite;
}
@-webkit-keyframes spin {
    0%   {
        -webkit-transform: rotate(0deg);
        -ms-transform: rotate(0deg);
        transform: rotate(0deg);
    }
    100% {
        -webkit-transform: rotate(360deg);
        -ms-transform: rotate(360deg);
        transform: rotate(360deg);
    }
}
@keyframes spin {
    0%   {
        -webkit-transform: rotate(0deg);
        -ms-transform: rotate(0deg);
        transform: rotate(0deg);
    }
    100% {
        -webkit-transform: rotate(360deg);
        -ms-transform: rotate(360deg);
        transform: rotate(360deg);
    }
}
</style>

<script>
 $(document).ready(function() {

    $("#generate-data").click(function() {       
        $( ".body" ).fadeOut( "fast" );
        $("#preloader").fadeIn("slow");

        $.ajax({    //create an ajax request to display.php
            type: "GET",
            url: "/generatedata",             
            dataType: "json",   //expect json to be returned                
            success: function(response){                    
                $("#preloader").fadeOut(0);
                $( ".body" ).fadeIn(2000);
                
                generateHtml(response);
            },
            error: function(response){
                $("#preloader").fadeOut(0);
                $( ".body" ).fadeIn(2000);
                
                $("#result-box").empty();
                $("#result-box").append('<p style="color:red">Try Again!</p>');
            }

        });
    });
});

function generateHtml(response) {
    var container = $("#result-box");
    //delete previous nodes
    container.empty();
    questions = response['data'];
    _.map(questions, function(q,k){
        container.append(createDOM(q,k));
    });
    
}

function createDOM(q,k) {
    var innerdom = '<div class="panel-body question">Question: '+q.prompt+'</div><div class="panel-body answer">Answer: '+q.answer+'</div><div class="panel-body options">Options: '+q.options+'</div>';

    var outerdiv = $("<div>",{class: 'panel panel-default mt-2',id:'box_'+k, html: innerdom});
    return outerdiv;
}

</script>