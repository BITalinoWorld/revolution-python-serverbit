    var dev_list = {}
    var dev_entry = []
    var num_devices = 1
    var terminal_cmd = ""

    document.addEventListener('DOMContentLoaded', function() {
      $("#continue").hide()
      var f = document.getElementById("chn_field");
      var inputs = f.getElementsByTagName("input")
      for (var i = 1; i <= inputs.length; i++){
        clicked(i)
      }
      $("#device-s").prop("value", $("label[for='device-s']").html()).change();
      $("label[for='device-s']").html("Device List");
      $("#chn_field, #lbl_field, .input_toggle").hide();
      $("#protocol-s, #ip_address-s, #port-s, label[for='ip_address-s'], label[for='port-s'], label[for='protocol-s'").show();

      $('#import_json').hide()
      $('.hideable_img').hide();
      });

    $("#select_json_file").change(function(){
       $('#import_json').show()
     });

    $('#device-list').addInputArea({
        maximum : 10,
        area_del: '.del-area',
        after_add: function () {
            num_devices = $('select.dev_selector').length;
            var new_id = (num_devices-1).toString();
            var new_dropdown = $('select.dev_selector').last();
            var new_dropdown_id = "mySelect_".concat((num_devices-1).toString());
            new_dropdown.prop("id", new_dropdown_id);
            new_dropdown.change(function() {
                update_device_type(document.getElementById(new_dropdown.attr("id")), new_id);
            })
        }
    });

	function server_handler(device_finder) {
    var str_out = ""
		document.getElementById("find_devices").disabled = $('input[name="finder[]"]:checked').length == 0
		if (device_finder.id === "BITalino_check")
      if (device_finder.checked)
        $("#chn_field, #lbl_field, #buffer_size-s, #sampling_rate-s").show("fast");
      else
        $("#chn_field, #lbl_field, #buffer_size-s, #sampling_rate-s").hide("fast");
      var str_out = device_finder.checked ? "Initializing PLUX device finder" : "Disabled PLUX device finder";
		if (device_finder.id === "Riot_check")
      var str_out = device_finder.checked ? "Initializing OSC server for R-IOT" : "Disabled OSC server for R-IOT";
      if (device_finder.checked)
        start_osc_server()
      else
        debug_text(str_out, false);
    console.log(str_out)
	}

	function update_device_list(dl) {
  	$("select.dev_selector").each(function(){
        $('#'.concat(this.id.toString())).find('option').not(':first').remove();
        var my_dropdown = document.getElementById((this.id).toString())
        if (dl.size == 0){
            return
        }
        dl.forEach(function(dev) {
            var option = document.createElement("option");
            option.text = dev[0];
            option.value = dev[0];
            option.id = dev[1];
            my_dropdown.add(option)
        });
    });
		$('.hideable_img').hide('slow');
	}

  if ($("#device-s").val() === "WINDOWS-XX:XX:XX:XX:XX:XX|MAC-/dev/tty.BITalino-XX-XX-DevB"){
    $("#device-s").val("")
    $("#device_0").val("")
  }

  $("#update-device-list").click(function() {
    dev_entry = []
    for (i = 0; i < $("select.dev_selector").length; i++){
      var addr = $("#device_"+i).val()
      if (!dev_entry.includes(addr))
        dev_entry.push(addr)
    }
    dev_entry = dev_entry.filter(e => typeof e === 'string' && e !== '')
    $("#device-s").prop('value', arrayToString(dev_entry.toString())).change();
  })

	function update_device_type( d , d_id){
    var device_id = "device_".concat(d_id);
    var devicetype_id = "devicetype_".concat(d_id);
		document.getElementById(device_id).value = d.value;
		document.getElementById(devicetype_id).value = d.options[d.selectedIndex].id;
	}

  $("#device-s").change(function() {
    if ($("#device-s").val() === "WINDOWS-XX:XX:XX:XX:XX:XX|MAC-/dev/tty.BITalino-XX-XX-DevB"){
      $("#device-s").val("")
      $("#device_0").val("")
    }
    $("#dev_list_area").prop("value", $("#device-s").val())
  })

	var device_clicked = document.getElementById("mySelect_0");
    update_device_type(device_clicked, 0);
	device_clicked.addEventListener('change', function(event) {
		update_device_type(device_clicked, 0);
	});

	function clicked(buttonNumber){
		if($('#ch'+buttonNumber).prop('checked')){
      $('#'+$(".lbToggle")[buttonNumber-1].id).textinput('enable')
			// $('#lbA'+buttonNumber).textinput('enable')
		} else {
      $('#'+$(".lbToggle")[buttonNumber-1].id).textinput('disable')
			// $('#lbA'+buttonNumber).textinput('disable')
		}
	}

	function hasNumber(myString) {
  	     return /\d/.test(myString);
	}

  function addID(myString, id) {
  	     return myString.concat(id.toString());
	}

  function start_osc_server() {
    debug_text("Initializing OSC server for R-IOT", true);
    var web_console_url = 'http://localhost:9001/v1/console'
    $.ajax({
        url: web_console_url,
        type: 'GET',
        async: 'true',
        dataType: 'json',
        success:function(data){
          debug_text(data, true);
        },
        error: function (request,error) {
          debug_text(error);
        }
    });
  }

  $("#continue").click(function (e) {
    var web_console_url = 'http://localhost:9001/v1/console'
    cmd = JSON.stringify( $("#console_output").val() )
    $.ajax({
        url: web_console_url,
        type: 'POST',
        async: 'true',
        dataType: 'json',
        data: cmd,
        success:function(data){
          debug_text(data, true);
        },
        error: function (request,error) {
          debug_text(error);
        }
      });
  });

	$("#find_devices").click(function (e) {
        e.preventDefault();
        e.stopImmediatePropagation();
        var device_list_url = 'http://localhost:9001/v1/devices'
				var json_device_finder = {
							"Bluetooth": $('input[name="finder[]"]')[0].checked,
							"OSC": $('input[name="finder[]"]')[1].checked,
              "OSC_config": ['192.168.1.100', 8888]
						};
				console.log(json_device_finder)
				$.ajax({
						url: device_list_url,
						type: 'POST',
						async: 'true',
						dataType: 'json',
						data: JSON.stringify(json_device_finder),
            error: function (request,error) {
              debug_text(error);
            }
				});
				$('#loading_anim').show('fast');
        $.getJSON(device_list_url).done( function (response) {
                    dev_list = response['dev_list'];
                    update_device_list(dev_list);
            });
    });

  $(document).on('submit', function(){
      var dev_str = $("#device-s").val()
      if (dev_str == "" || (dev_str[0] != '[' && dev_str[dev_str.length - 1] != ']')){
  			alert("Please select a BITalino device in Device Selection and update device list")
  			window.location.href = 'http://localhost:9001/config'
  			return 0;
  		}
  		var entry_inputs = {}
  		var lbz = []
  		var chnz = []

  		var f = document.getElementById("lbl_field");
  		var inputs = f.getElementsByTagName("input");
  		for (var i = 0; i < inputs.length; i++){
        lbz.push(inputs[i].value.replace(/'/g, '"'));
  			if (!inputs[i].disabled){
  				if (i > 4){
  					chnz.push( i-4 )
  				}
  			}
  		}
  		console.log(lbz)

  		var fields = document.getElementById("config").querySelectorAll("label");
  		for (var i = 0; i <= fields.length; i++){
  			if (typeof fields[i] !== 'undefined') {
  				var key = fields[i].htmlFor
  				if (hasNumber(key) == false && key.slice(-2) === '-s'){
  					var input = document.getElementById(key);
  					if (input !== null){
  						// console.log(input.value)
  						entry_inputs[key] = input.value
  					}
  				}
  			}
  		}
  		console.log(entry_inputs)

  		json_entry_inputs = {
  			"device": entry_inputs["device-s"],
  			"sampling_rate": entry_inputs["sampling_rate-s"],
  			"buffer_size": entry_inputs["buffer_size-s"],
  			"ip_address": JSON.stringify(entry_inputs["ip_address-s"]),
  			"port": entry_inputs["port-s"],
  			"protocol": entry_inputs["protocol-s"],
  			"channels": chnz,
  			"labels": lbz
  		};
      console.log(json_entry_inputs["ip_address"])

  		$.ajax({
  			type: "POST",
  			url: 'http://localhost:9001/v1/configs',
  			async: 'true',
  			data: JSON.stringify(json_entry_inputs),
  			// data: '{"device": "'+dev+'", "sampling_rate":'+fs+', "buffer_size":'+bs+', "port":'+port+', "labels":"'+lbz+'", "channels":"'+ chnz +'"}',
  			success: function (result) {
  				window.location.href = 'http://localhost:9001/v1/configs'
  			},
  			error: function (request,error) {
  				alert(request.responseText);
          window.location.href = 'http://localhost:9001/v1/'
  			}
  		})
  	});

  $("#import_json").click(function (e) {
    var files = document.getElementById('select_json_file').files;
    if (files.length <= 0) {
      return false;
    }
    var fr = new FileReader();
      fr.onload = function(e, isLast) {
        if (IsJsonString(e.target.result) == false){
          debug_text("invalid config file")
          return
        }
        var file_name = $("#select_json_file").val().replace(/^.*[\\\/]/, '')
        var result = JSON.parse(e.target.result);
        var formatted = JSON.stringify(result, null, 2);
        $.each(result, function (key, value) {
            var form_input_id = key.toString().concat('-s')
            var form_input_element = $("#".concat(form_input_id))
            // console.log(form_input_element)
            if (key === "channels"){
              var f = document.getElementById("chn_field");
              var chns = f.getElementsByTagName("input")
              chns = Array.prototype.slice.call(chns);
              chns.forEach(function(chn) {
                if (chn.checked) chn.click()
              })
              value.forEach(function(chn_num) {
                chns[chn_num-1].click()
                clicked(chn_num)
              })
            }
            if (key === "labels"){
              var f = document.getElementById("lbl_field");
              var lbls = f.getElementsByTagName("input")
              lbls = Array.prototype.slice.call(lbls);
              for (var i = 0; i < value.length; i++) {
                lbls[i].value = value[i]
                var buttonLbl = 'ch'+(i+1);
                $("label[for='"+buttonLbl+"']").html("Channel "+value[i+5])
              }
            }
            if ( form_input_element.length == 0 ){
              debug_text("invalid config file")
              return 0
            }
            form_input_element.prop('value', value).change();
            if (key === "device"){
              console.log(value)
              $("#device-s").prop('value', JSON.stringify(value)).change();
            }
            debug_text(file_name + " loaded");
        });
        }
        fr.readAsText(files.item(0));
    });

	document.getElementById("reset_config").addEventListener("click", function(){
		console.log("reset")
		$.ajax({
			type: "POST",
			url: 'http://localhost:9001/v1/configs',
			async: 'true',
			data: JSON.stringify("restored config.json"),
			success: function (result) {
				alert(result)
			},
			error: function (request,error) {
				// This callback function will trigger on unsuccessful action
				alert(request.responseText)
			}
		})
	});

  function debug_text(str, show_btn=false){
    $("#console_output").val(str);
    if (show_btn)
      $("#continue").show()
    else
      $("#continue").hide()
  }

  function arrayToString(array) {
    return '['.concat(array).concat(']')
  }

  function IsJsonString(str) {
    try {
        JSON.parse(str);
    } catch (e) {
        return false;
    }
    return true;
}
