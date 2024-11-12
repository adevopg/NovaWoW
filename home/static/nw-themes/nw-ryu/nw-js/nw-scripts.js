function nwNavBar() {
  var x = document.getElementById('nw-nav-bar');
  if (x.className === 'nav-bar') {
    x.className += ' responsive';
  } else {
    x.className = 'nav-bar';
  }

  var y = document.getElementById('menu-icon');
  y.classList.toggle('change');
}

function nwIcon() {
  var x = document.getElementById('right-content-min');
  if (x.className === 'right-content') {
    x.className += ' responsive';
  } else {
    x.className = 'right-content';
  }
}

function changeButton(button, name) {
    button.html(''+name+'');
    button.css({'color': '#b1997f',
                'background-color':'hsla(0,0%,100%,0.1)',
                'cursor':'default'
    });
    button.prop('disabled',true);
}

function restoreButton(button, buttonoriginal) {
    $(button).html(buttonoriginal);
    $(button).removeAttr('style');
    $(button).prop('disabled',false);
};
