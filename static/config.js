    var dev_list = {}
    var num_devices = 1
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
                console.log(new_id);
                updateDeviceType(document.getElementById(new_dropdown.attr("id")), new_id);
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
	if (dl.size == 0){
			return
  	}
  	$("select.dev_selector").each(function(){
        $(this.id).find('option').not(':first').remove();
        var my_dropdown = document.getElementById((this.id).toString())
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

	function updateDeviceType( d , d_id){
    var device_id = "device_".concat(d_id);
    var devicetype_id = "devicetype_".concat(d_id);
		document.getElementById(device_id).value = d.value;
		document.getElementById(devicetype_id).value = d.options[d.selectedIndex].id;
	}

	var device_clicked = document.getElementById("mySelect_0");
    updateDeviceType(device_clicked, 0);
	device_clicked.addEventListener('change', function(event) {
		updateDeviceType(device_clicked, 0);
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

	document.addEventListener('DOMContentLoaded', function() {
		// update_device_list(dev_list)
		var f = document.getElementById("chn_field");
		var inputs = f.getElementsByTagName("input")
		for (var i = 1; i <= inputs.length; i++){
			clicked(i)
		}
    });

    function get_device_list(json_response){
        $.getJSON(json_response).done(function(response) {
                    dev_list = response['dev_list']
                    update_device_list(dev_list)
            })
    }

	$('.hideable_img').hide();
	$("#find_devices").click(function (e) {
        e.preventDefault();
        e.stopImmediatePropagation();
				var json_device_finder = {
							"Bitalino": $('input[name="finder[]"]')[0].checked.toString(),
							"Riot": $('input[name="finder[]"]')[1].checked.toString()
						};
				console.log(json_device_finder)
				$.ajax({
						url: 'http://localhost:9001/v1/devices',
						type: 'POST',
						async: 'true',
						dataType: 'json',
						data: JSON.stringify(json_device_finder)
				});
				$('#loading_anim').show('fast');
				var device_list_url = 'http://localhost:9001/v1/devices'
        $.ajax({
            url: device_list_url,
            type: 'GET',
            dataType: 'jsonp',
				})
        $.getJSON(device_list_url).done( function (response) {
                    dev_list = response['dev_list'];
                    update_device_list(dev_list);
            });
    });

$(document).on('submit', function( e ){
		$("select.dev_selector").each(function(){
			var my_dropdown = document.getElementById((this.id).toString())
			if (my_dropdown.value == ""){
				alert("Please select a BITalino device in Device Selection")
				window.location.href = 'http://localhost:9001/config'
				return false;
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
				if (hasNumber(key) == false){
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
			"device": entry_inputs["device_s"],
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
