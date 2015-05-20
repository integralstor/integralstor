from django import forms

class AddNodesForm(forms.Form):
  """ Form for adding one or more peers to the pool"""

  def __init__(self, *args, **kwargs):
    #assert False
    scl = []
    if kwargs :
      anl = kwargs.pop('addable_node_list')
    super(AddNodesForm, self).__init__(*args, **kwargs)
    ch = []
    for d in anl:
      tup = (d["hostname"], d["hostname"])
      ch.append(tup)   
    self.fields["nodes"] = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=ch)

class RemoveNodeForm(forms.Form):
  """ Form for removing a peer from a pool"""

  def __init__(self, *args, **kwargs):
    sled_list = []
    if kwargs :
      node_list = kwargs.pop('node_list')
    super(RemoveNodeForm, self).__init__(*args, **kwargs)
    ch = []
    for node in node_list:
      tup = (node, node)
      ch.append(tup)   
    self.fields["node"] = forms.ChoiceField(widget=forms.RadioSelect(), choices=ch)

class RemoveNodeConfForm(forms.Form):

  node = forms.CharField()

