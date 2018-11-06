    var dev_list = {}
    var dev_entry = []
    var num_devices = 1

    document.addEventListener('DOMContentLoaded', function() {
      // update_device_list(dev_list)
      var f = document.getElementById("chn_field");
      var inputs = f.getElementsByTagName("input")
      for (var i = 1; i <= inputs.length; i++){
        clicked(i)
      }
      $("#devinput-s").prop("value", $("label[for='devinput-s']").html());
      $("label[for='devinput-s']").html("Device List");
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
		document.getElementById("find_devices").disabled = $('input[name="finder[]"]:checked').length == 0
		if (device_finder.id === "BITalino_check")
			if (device_finder.checked)
				console.log("Initializing PLUX device finder")
			else
				console.log("Disable PLUX device finder")
		if (device_finder.id === "Riot_check")
			if (device_finder.checked)
				console.log("Initializing OSC server for R-IOT")
			else
				console.log("Disable OSC server for R-IOT")
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

	if (document.getElementById("device_0").value === "WINDOWS-XX:XX:XX:XX:XX:XX|MAC-/dev/tty.BITalino-XX-XX-DevB"){
		document.getElementById("device_0").value = ""
	}

  function update_device_entry( addr ){
    dev_entry.push(addr);
    dev_entry = dev_entry.filter(e => typeof e === 'string' && e !== '')
    $("#devinput-s").val(dev_entry);
  }

	function update_device_type( d , d_id){
    update_device_entry(d.value)
    var device_id = "device_".concat(d_id);
    var devicetype_id = "devicetype_".concat(d_id);
		document.getElementById(device_id).value = d.value;
		document.getElementById(devicetype_id).value = d.options[d.selectedIndex].id;
    if (document.getElementById(devicetype_id).value === "bitalino"){
      $("#chn_field, #lbl_field, .input_toggle").show("fast");
    }
	}

	var device_clicked = document.getElementById("mySelect_0");
    update_device_type(device_clicked, 0);
	device_clicked.addEventListener('change', function(event) {
		update_device_type(device_clicked, 0);
	});

	function clicked(buttonNumber){
		if($('#ch'+buttonNumber).prop('checked')){
			$('#lbA'+buttonNumber).textinput('enable')
		} else {
			$('#lbA'+buttonNumber).textinput('disable')
		}
	}

	function hasNumber(myString) {
  	     return /\d/.test(myString);
	}

  function addID(myString, id) {
  	     return myString.concat(id.toString());
	}

	$("#find_devices").click(function (e) {
        e.preventDefault();
        e.stopImmediatePropagation();
        var device_list_url = 'http://localhost:9001/v1/devices'
				var json_device_finder = {
							"Bluetooth": $('input[name="finder[]"]')[0].checked.toString(),
							"OSC": $('input[name="finder[]"]')[1].checked.toString(),
              "OSC_config": ['192.168.1.100', 8888]
						};
				console.log(json_device_finder)
				$.ajax({
						url: device_list_url,
						type: 'POST',
						async: 'true',
						dataType: 'json',
						data: JSON.stringify(json_device_finder)
				});
				$('#loading_anim').show('fast');
        
        $.getJSON(device_list_url).done( function (response) {
                    dev_list = response['dev_list'];
                    update_device_list(dev_list);
            });
    });

$(document).on('submit', function(){
		$("select.dev_selector").each(function(){
			var my_dropdown = document.getElementById((this.id).toString())
			if (my_dropdown.value == ""){
				alert("Please select a BITalino device in Device Selection")
				window.location.href = 'http://localhost:9001/config'
				return 0;
			}
		})
		var entry_inputs = {}
		var lbz = []
		var chnz = []

		var f = document.getElementById("lbl_field");
		var inputs = f.getElementsByTagName("input")
		for (var i = 0; i < inputs.length; i++){
			if (!inputs[i].disabled){
				lbz.push(inputs[i].value)
				if (i > 4){
					chnz.push( i-4 )
				}
			}
		}
		console.log(chnz.slice(5))

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
			"device": entry_inputs["devinput-s"],
			"sampling_rate": entry_inputs["sampling_rate-s"],
			"buffer_size": entry_inputs["buffer_size-s"],
			"ip_address": entry_inputs["ip_address-s"],
			"port": entry_inputs["port-s"],
			"protocol": entry_inputs["protocol-s"],
			"channels": chnz,
			"labels": lbz
		};

		$.ajax({
			type: "POST",
			url: 'http://localhost:9001/v1/configs',
			async: 'true',
			data: JSON.stringify(json_entry_inputs),
			// data: '{"device": "'+dev+'", "sampling_rate":'+fs+', "buffer_size":'+bs+', "port":'+port+', "labels":"'+lbz+'", "channels":"'+ chnz +'"}',
			success: function (result) {
				alert("redirecting to ClientBIT")
				window.location.href = 'http://localhost:9001/v1/configs'
			},
			error: function (request,error) {
				// This callback function will trigger on unsuccessful action
				alert(request.responseText);
			}
		})
	});

  $(document).on('submit', function(){
  		$("select.dev_selector").each(function(){
  			var my_dropdown = document.getElementById((this.id).toString())
  			if (my_dropdown.value == ""){
  				alert("Please select a BITalino device in Device Selection")
  				window.location.href = 'http://localhost:9001/config'
  				return 0;
  			}
  		})
  		var entry_inputs = {}
  		var lbz = []
  		var chnz = []

  		var f = document.getElementById("lbl_field");
  		var inputs = f.getElementsByTagName("input")
  		for (var i = 0; i < inputs.length; i++){
  			if (!inputs[i].disabled){
  				lbz.push(inputs[i].value)
  				if (i > 4){
  					chnz.push( i-4 )
  				}
  			}
  		}
  		console.log(chnz.slice(5))

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
  			"device": entry_inputs["devinput-s"],
  			"sampling_rate": entry_inputs["sampling_rate-s"],
  			"buffer_size": entry_inputs["buffer_size-s"],
  			"ip_address": entry_inputs["ip_address-s"],
  			"port": entry_inputs["port-s"],
  			"protocol": entry_inputs["protocol-s"],
  			"channels": chnz,
  			"labels": lbz
  		};

  		$.ajax({
  			type: "POST",
  			url: 'http://localhost:9001/v1/configs',
  			async: 'true',
  			data: JSON.stringify(json_entry_inputs),
  			// data: '{"device": "'+dev+'", "sampling_rate":'+fs+', "buffer_size":'+bs+', "port":'+port+', "labels":"'+lbz+'", "channels":"'+ chnz +'"}',
  			success: function (result) {
  				alert("redirecting to ClientBIT")
  				window.location.href = 'http://localhost:9001/v1/configs'
  			},
  			error: function (request,error) {
  				// This callback function will trigger on unsuccessful action
  				alert(request.responseText);
  			}
  		})
  	});

  $("#import_json").click(function (e) {
    var files = document.getElementById('select_json_file').files;
    console.log(files);
    if (files.length <= 0) {
      return false;
  }
  var fr = new FileReader();
    fr.onload = function(e) {
      var result = JSON.parse(e.target.result);
      var formatted = JSON.stringify(result, null, 2);
  		console.log(formatted);
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
