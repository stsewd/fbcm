/*jshint esversion: 6 */

function createAlert(type, msg) {
  var icon = type === 'alert-success' ? 'glyphicon-ok' : 'glyphicon-warning-sign';
  var alertBootstrap = $('<div>', {
    'class': `alert ${type} fade in alert-dismissible`,
    'role': 'alert',
    'hidden': 'hidden',
    'html': `
      <button type="button" class="close" data-dismiss="alert">
      <span>&times;</span>
      </button>
      <span class="alert-message">
      <span class="glyphicon ${icon} text-muted"></span> ${msg}
    </span>`
  });
  $('#container-alert').append(alertBootstrap);
  return alertBootstrap;
}

function showAlert(type, msg) {
  var alertBootstrap = createAlert(type, msg);
  alertBootstrap.show();
  alertBootstrap.delay(3500).slideUp(300, function () {
    $(this).alert('close');
  });
}

function sendRequest(form, method, url, success) {
  $(form).submit(function (e) {
    $.ajax({
      'type': method,
      'url': url,
      'data': $(this).serialize(),
      'beforeSend': function () {
        $('.loader-container').show();
      },
      'success': function (data, status) {
        if (data.status && data.status === 'error') {
          showAlert('alert-danger', data.description);
        } else {
          success(data, status);
        }
      },
      'error': function (data) {
        showAlert('alert-danger', 'Ups, algo inesperado ocurrió.');
      },
      'complete': function () {
        $('.loader-container').hide();
      }
    });
    e.preventDefault();
  });
}

$(document).ready(function () {
  $(document).pjax('a', '#main-content');
});
