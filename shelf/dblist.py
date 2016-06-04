Rock forming
Cement
Chemin
Pigment

                                      qtarget = "Co",
                                      qlambda=0,
                                      available = phaselist.availablePhases,
                                      selected = phaselist.defaultPhases,
                                      fwhma = a,
                                      fwhmb = b


                a = -0.001348 
                b =  0.352021 
                                      
<div class="form-group">
  <label for="sel1">Select Mode:</label>
  <select class="form-control" id="sel1">
    {%- for m in modes %}
    <option>{{ m.title }}</option>
    {%- endfor %}
  </select>
</div>
