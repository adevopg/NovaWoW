if(window.history.replaceState){window.history.replaceState(null,null,window.location.href);};$(function(){$('select').on('change',function(){var select=$(this);select.css('color',select.children('option:selected').css('color'));});});$(function(){$('#trade-sell-a').on('click',function(){$('#trade-sell-div').fadeIn('slow');$('#trade-buy-div').hide();});$('#trade-buy-a').on('click',function(){$('#trade-buy-div').fadeIn('slow');$('#trade-sell-div').hide();});});$(function(){$(".toggle-password").click(function(){$(this).toggleClass("fa-eye fa-eye-slash");var type=$(this).hasClass("fa-eye-slash")?"text":"password";$("#password-sell").attr("type",type);});});$(function(){$(".toggle-password").click(function(){$(this).toggleClass("fa-eye fa-eye-slash");var type=$(this).hasClass("fa-eye-slash")?"text":"password";$("#password-buy").attr("type",type);});});$(function(){$(".toggle-token").click(function(){$(this).toggleClass("fa-eye fa-eye-slash");var type=$(this).hasClass("fa-eye-slash")?"text":"password";$("#security-token-sell").attr("type",type);});});$(function(){$(".toggle-token").click(function(){$(this).toggleClass("fa-eye fa-eye-slash");var type=$(this).hasClass("fa-eye-slash")?"text":"password";$("#security-token-buy").attr("type",type);});});$(function(){$('.trade-points-sell-button').on('click',function(e){e.preventDefault();e.stopPropagation();$("#trade-points-sell-response").empty();var button=$(this);var buttonoriginal=button.html();var data={tradepointssell:button.data('id')};data=$("#uw-trade-points-sell-form").serialize()+'&'+$.param(data);changeButton(button,'CREANDO CÓDIGO');$.ajax({type:'POST',url:'',data:data,dataType:'json',success:function(data){$("#trade-points-sell-response").append(data.message).hide().slideDown();if(data.success===true){button.html("CÓDIGO CREADO");button.css("color","#d79602");setTimeout(function(){$("#uw-trade-points-sell-form")[0].reset();restoreButton(button,buttonoriginal);grecaptcha.reset(0);},5000);}
else{setTimeout(function(){$("#trade-points-sell-response").slideUp(function(){$("#trade-points-sell-response").empty();restoreButton(button,buttonoriginal);grecaptcha.reset(0);});},5000);}},error:function(){setTimeout(function(){alert("Algo ha salido mal. Por favor intente más tarde");window.location.reload();},2000);}});});});$(function(){$('.trade-points-buy-button').on('click',function(e){e.preventDefault();e.stopPropagation();$("#trade-points-buy-response").empty();$(".trade-points-check-button").prop('disabled',true);var button=$(this);var buttonoriginal=button.html();var data={tradepointsbuy:button.data('id')};data=$("#uw-trade-points-buy-form").serialize()+'&'+$.param(data);changeButton(button,'CANJEANDO CÓDIGO');$.ajax({type:'POST',url:'',data:data,dataType:'json',success:function(data){$("#trade-points-buy-response").append(data.message).hide().slideDown();if(data.success===true){button.html("CÓDIGO CANJEADO");button.css("color","#d79602");setTimeout(function(){$("#uw-trade-points-buy-form")[0].reset();$(".trade-points-check-button").prop('disabled',false);restoreButton(button,buttonoriginal);grecaptcha.reset(1);},5000);}
else{setTimeout(function(){$("#trade-points-buy-response").slideUp(function(){$("#trade-points-buy-response").empty();$(".trade-points-check-button").prop('disabled',false);restoreButton(button,buttonoriginal);grecaptcha.reset(1);});},5000);}},error:function(){setTimeout(function(){alert("Algo ha salido mal. Por favor intente más tarde");window.location.reload();},2000);}});});});$(function(){$('.trade-points-check-button').on('click',function(e){e.preventDefault();e.stopPropagation();$("#trade-points-buy-response").empty();$(".trade-points-buy-button").prop('disabled',true);var button=$(this);var buttonoriginal=button.html();var data={tradepointscheck:button.data('id')};data=$("#uw-trade-points-buy-form").serialize()+'&'+$.param(data);changeButton(button,'CHEQUEANDO CÓDIGO');$.ajax({type:'POST',url:'',data:data,dataType:'json',success:function(data){$("#trade-points-buy-response").append(data.message).hide().slideDown();if(data.success===true){button.html("INFO DEL CÓDIGO");button.css("color","#d79602");setTimeout(function(){$(".trade-points-buy-button").prop('disabled',false);restoreButton(button,buttonoriginal);grecaptcha.reset(1);},5000);}
else{setTimeout(function(){$("#trade-points-buy-response").slideUp(function(){$("#trade-points-buy-response").empty();$(".trade-points-buy-button").prop('disabled',false);restoreButton(button,buttonoriginal);grecaptcha.reset(1);});},5000);}},error:function(){setTimeout(function(){alert("Algo ha salido mal. Por favor intente más tarde");window.location.reload();},2000);}});});});