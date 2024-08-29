$("#click_btn").click(function(){
  if(!$( "#tab-two" ).hasClass("show active")){
       $("#tab-one").removeClass("show active");
       $("#tab-two").addClass("show active");
    }
    else{
        $("#tab-two").addClass("show active");
        $("#tab-one").removeClass("show active");
    }
});

$("#todos-tab").click(function(){
  if($( "#tab-one").hasClass( "show active" )){
       $("#tab-two").removeClass("show active");
       $("#tab-one").addClass("show active");
    }
    else{
        $("#tab-one").addClass("show active");
        $("#tab-two").removeClass("show active");
    }
});

$("#two_tab").click(function(){
    if($( "#click_btn").hasClass( "active" )){
        $("#todos-tab").removeClass("active");
        $("#click_btn").addClass("active");
    }
      else{
        $("#todos-tab").removeClass("active");
        $("#click_btn").addClass("active");
    }
});

$("#one_tab").click(function(){
    if($( "#todos-tab").hasClass( "active" )){
        $("#click_btn").removeClass("active");
        $("#todos-tab").addClass("active");
    }
      else{
        $("#click_btn").removeClass("active");
        $("#todos-tab").addClass("active");
    }
});

//? setpinmodel //
$("#change_pin_button").click(function(){
    $("#SetPinModel").css("display", "block")
    $("#SetPinModel").addClass("show");
    $("#SetPinModel").attr("aria-hidden", "false");
});

$("#close_set_pin_model").click(function(){
    $("#SetPinModel").css("display", "none")
    $("#SetPinModel").removeClass("show");
    $("#SetPinModel").attr("aria-hidden", "true");
});


// rechargepinmodel //
$("#recharge_card_button").click(function(){
    $("#RechargeCardModel").css("display", "block")
    $("#RechargeCardModel").addClass("show");
    $("#RechargeCardModel").attr("aria-hidden", "false");
});

$("#close_recharge_model").click(function(){
    $("#RechargeCardModel").css("display", "none")
    $("#RechargeCardModel").removeClass("show");
    $("#RechargeCardModel").attr("aria-hidden", "true");
});
