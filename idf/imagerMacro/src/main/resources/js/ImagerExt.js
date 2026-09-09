var imagerMacroInitExt = function(inA)
{
	imagerMacroInitTopExt();
	imagerMacroInitBottomExt();
	//imagerMacroInitMiddleExt();
}
var imagerMacroInitMiddleExt = function(inA)
{
        var simple = new Ext.FormPanel({
            border:false,
            hidden:false,
            margin: '20 0 20 0',
            layout: 'hbox',
            items: [{
                xtype: "panel",
                margin: '0 10 0 0',
                html: "Here is the space for buttons"},
                {xtype: "button",
                margin: '0 10 0 0',
                text: "TBD",
                handler: function(){
				   var url =ijfUtils.replaceKeyValues(inField.dataSource,item);
				   window.open(url);
            	}}]
        });
  	     var tElement = document.getElementById("imagerDivMiddleId");
      simple.render(tElement);
}
var imagerMacroInitTopExt = function(inA)
{

   var tFields = [];
   var listColumns = [];

	tFields.push({name: "id", type: 'string'});
	listColumns.push({
			header: "id",
			sortable: true,
			hidden: true,
			width: 20,
			dataIndex: "id",
			filter: {
				type: 'string'
			}
		});
	tFields.push({name: "selversion", type: 'string'});
	listColumns.push({
			header: "selver",
			sortable: true,
			hidden: true,
			width: 20,
			dataIndex: "selversion",
			filter: {
				type: 'string'
			}
		});
	tFields.push({name: "rawtitle", type: 'string'});
	listColumns.push({
			header: "rtitle",
			sortable: true,
			hidden: true,
			width: 20,
			dataIndex: "rawtitle",
			filter: {
				type: 'string'
			}
		});

   tFields.push({name: 'chkbx', type: 'boolean'});
	listColumns.push({
			header: "<input type='checkbox' onclick='imagerMacroHeaderTopChecked(this);'>",
			sortable: false,
			hidden: false,
			xtype: 'checkcolumn',
			centered:true,
			width: 50,
			dataIndex: 'chkbx',
			listeners: {
				checkchange: function(n,o,f)
				{
					null;
				}
			}
	});

	tFields.push({name: "title", type: 'string'});
	listColumns.push({
			header: "Title",
			sortable: true,
			hidden: false,
			width: '30%',
			dataIndex: "title",
			filter: {
				type: 'string'
			}
		});
	tFields.push({name: "space", type: 'string'});
	listColumns.push({
			header: "Space",
			sortable: true,
			hidden: false,
			width: '22%',
			dataIndex: "space",
			filter: {
				type: 'string'
			}
		});
	tFields.push({name: "sourcePageId", type: 'string'});
	listColumns.push({
			header: "SourceId",
			sortable: true,
			hidden: true,
			width: 20,
			dataIndex: "sourcePageId",
			filter: {
				type: 'string'
			}
		});

	tFields.push({name: "targetParentPageId", type: 'string'});
	listColumns.push({
			header: "ParentId",
			sortable: true,
			hidden: true,
			width: 20,
			dataIndex: "targetParentPageId",
			filter: {
				type: 'string'
			}
		});

	tFields.push({name: "psrPageId", type: 'string'});
	listColumns.push({
			header: "psrPageId",
			sortable: true,
			hidden: true,
			width: 20,
			dataIndex: "psrPageId",
			filter: {
				type: 'string'
			}
		});

	tFields.push({name: "versions", type: 'number'});
	listColumns.push({
			header: "Count",
			sortable: true,
			hidden: false,
			format: "0,000",
			xtype: 'numbercolumn',
			width: '10%',
			dataIndex: "versions",
			filter: {
				type: 'number'
			}
		});

		tFields.push({name: "vdates", type: 'string'});
		var lookup = []

				//var vers = imagerMacroGetPageVersionsById(p.id);
				//var lookup = vers.map(function(e)
				//{
				//	return [e.number,moment(e.when)];
			    //});
			Ext.define('imagerMacroVersionDropdownId', {
						extend: 'Ext.data.Model',
						fields: [{name:'vnum', type: 'string'},
								 {name: 'vdate', type: 'string'}]
			});
			var lookup = Ext.create('Ext.data.Store', {
				model: 'imagerMacroVersionDropdownId',
				autoLoad: false,
				proxy: {
					type: 'ajax',
					url: '/rest/experimental/content/tbd/version',
					extraParams : '',
					filterParam: '',
					groupParam: '',
					limitParam: '',
					pageParam: '',
					sortParam: '',
					startParam: '',
					reader: {
						type: 'json',
						transform: function(data) {
								// do some manipulation of the raw data object
								 data.results = data.results.map(function(i){
											var retObj ={};
											retObj.vnum= i.number;
											retObj.vdate = moment(i.when).format('M/D/YYYY HH:mm');
											retObj.rawdate = moment(i.when)
											return retObj;
								 });

							return data.results;
						}
					}
				}
			});

	tFields.push({name: "images", type: 'string'});
	listColumns.push({
			header: "Compare To",
			sortable: true,
			hidden: false,
			//xtype: 'datecolumn',
			renderer: function(inVal){if(!inVal) return null; return moment(inVal).format('M/D/YYYY HH:mm');},
			width: '15%',
			dataIndex: "images",
			filter: {
				type: 'string'
			},
			editor: {
				completeOnEnter: true,
				field: {xtype: 'combobox',
							store: lookup,
							displayField: 'vdate',
							valueField: 'vnum',
							labelAlign: 'left',
							hideTrigger: false,
							triggerAction: 'all',
							queryMode: 'remote',
							selectOnFocus:true,
							listeners: {
								beforequery: function(queryPlan, eOpts )
								{
									//update the url with the current page
									var selection = gridPanel.getSelection();
									var targetId = selection[0].data.targetParentPageId;
									var targetTitle = selection[0].data.rawtitle;
									/*var targetParent = imagerMacroGetPageAndChildren(targetId);
									if(!targetParent)
									{
										Ext.Msg.alert("Error","Unable to acquire the children of the parent page");
										return;
									}
									//find the targetId from the target parent.
									var lTarget = "xxx";
									targetParent.children.page.results.forEach(function(p)
									{
										if(p.title == targetTitle + " (PSR)") lTarget = p.id;
									});*/
									lTarget = selection[0].data.psrPageId;
									var p = queryPlan.combo.getStore().getProxy();
									p.setUrl('/rest/experimental/content/'+lTarget+'/version');
									queryPlan.combo.getStore().reload();
								},
								focusleave: function(f,o,n)
								{
									var newVal = f.value;
									if(gridPanel.selection.get(f.name)==newVal) return;
									var tUpdate = function(){
										gridPanel.selection.set(f.name,f.rawValue);
										gridPanel.selection.set("selversion",f.value);
									}
									window.setTimeout(tUpdate,30);
								}
								,select: function(f,o,n)
								{
									var selection = gridPanel.getSelection();
									var sourceId = selection[0].data.sourcePageId;
									var targetId = selection[0].data.targetParentPageId;
									var sourceTarget = selection[0].data.rawtitle;
									var verId = f.value;
									var curVer = selection[0].data.versions;
									if(!verId)
									{
										Ext.Msg.alert("Info","Please select a version date first.");
										return;
									}
									/*
									var targetParent = imagerMacroGetPageAndChildren(targetId);
									if(!targetParent)
									{
										Ext.Msg.alert("Error","Unable to acquire the children of the parent page");
										return;
									}
									//find the targetId from the target parent.
									var lTarget = null;
									targetParent.children.page.results.forEach(function(p)
									{
										if(p.title == sourceTarget + " (PSR)") lTarget = p.id;
									});*/
									var lTarget=selection[0].data.psrPageId;
									if(!lTarget)
									{
										Ext.Msg.alert("Error","Unable to find the key page");
										return;
									}
								    var url = '/pages/diffpagesbyversion.action?pageId='+lTarget+'&originalVersion='+curVer+'&revisedVersion='+verId;
								    window.open(url);

								}
							}

				}
			}

		});


	tFields.push({name: "lastUpdated", type: 'date'});
	listColumns.push({
			header: "Last Updated",
			sortable: true,
			hidden: false,
			//xtype: 'datecolumn',
			renderer: function(inVal){ if(!inVal) return ""; return moment(inVal).format('M/D/YYYY HH:mm');},
			width: '15%',
			dataIndex: "lastUpdated",
			filter: {
				type: 'date'
			}
		});

		 Ext.define("imagerMacroTopDataModel", {
			 extend: 'Ext.data.Model',
			 fields: tFields
		 });

	     var gridStore = new Ext.data.Store({
	         model: "imagerMacroTopDataModel"
	     });


		var gridMenu = new Ext.menu.Menu({ items:
		[
				{ text: 'Open Version', handler: function()  {

						var selection = gridPanel.getSelection();
						var sourceId = selection[0].data.sourcePageId;
						var targetId = selection[0].data.targetParentPageId;
 					    var sourceTarget = selection[0].data.rawtitle;
 					    var verId = selection[0].data.selversion;
						if(!verId)
						{
							Ext.Msg.alert("Info","Please select a version date first.");
							return;
						}


						/*var targetParent = imagerMacroGetPageAndChildren(targetId);
						if(!targetParent)
						{
							Ext.Msg.alert("Error","Unable to acquire the children of the parent page");
							return;
						}
						//find the targetId from the target parent.
						var lTarget = null;
						targetParent.children.page.results.forEach(function(p)
						{
							if(p.title == sourceTarget + " (PSR)") lTarget = p.id;
						});*/
						var lTarget=selection[0].data.psrPageId;
						if(!lTarget)
						{
							Ext.Msg.alert("Error","Unable to find the key page");
							return;
						}

					   var getVersionRest = imagerMacroGetPageVersionRest(lTarget,verId);

					  //http://confluence.idealfed.com/rest/experimental/content/1867823/version/10
						if(!getVersionRest)
						{
							Ext.Msg.alert("Error","Unable to find the version url");
							return;
						}


					   var url = getVersionRest.content._links.webui;
	 				   window.open(url);

				} }
		]});

	 	var headerButtons =[];
	 		headerButtons.push({
	 						xtype:'button',
	 						style: "background:transparent;border:0px",
	 						text: 'HTML Report',
	 						scope: this,
	 						handler: function(){
	 							 //create record...
									var selection = gridPanel.getStore().getData();
									var lData = gridStore.getData();
									var htmlOut = "";
									lData.items.forEach(function(r)
									{
										var cb = r.get('chkbx');
										if(cb)
										{
											var sourceId = r.data.sourcePageId;
											var targetId = r.data.targetParentPageId;
											var sourceTarget = r.data.rawtitle;
											/*
											var targetParent = imagerMacroGetPageAndChildren(targetId);
											if(!targetParent)
											{
												return;
											}
											//find the targetId from the target parent.
											var lTarget = null;
											targetParent.children.page.results.forEach(function(p)
											{
												if(p.title == sourceTarget + " (PSR)") lTarget = p.id;
											});*/
											var lTarget=r.data.psrPageId;
											if(lTarget)
											{
												var sView = imagerMacroGetPageStyledView(lTarget);
												//process each page sep
												var pView =  sView.body.styled_view.value;
												//Look for Structure and clear out if there, leave params...
												var t = pView.split(/<iframe/g);
												for(var j = 1; j< t.length;j++)
												{
													var tt =t[j].split(/<\/iframe>/);
													// tt[0] is the contents of the iFrame....

													var src = tt[0].split(/ src=/);
													var p = src[1].split(/up_/g);
													var pars = {};
													for(var i = 1; i< p.length;i++)
													{
														var parts = p[i].split("&");
														var parts2 = parts[0].split("=");
														pars[parts2[0]]=parts2[1];
													}
													//replace iframe with <pre> of json
													pView=pView.replace("<iframe"+tt[0]+"</iframe>", "<pre>" + JSON.stringify(pars,0,4) + "</pre>");
													//console.log(JSON.stringify(pars,0,4));
												};

												if(sView) htmlOut+="<h1>"+sView.title+"</h1>" + pView;
											}
										}
									});
									if(!htmlOut)
									{
										Ext.Msg.alert("Info","No HTML to display, did you check rows?");
										return;
									}

    								var style = '<link type="text/css" href="/download/resources/com.idealfed.pageimager.imager:imager-resources/confluenceHtmlStyles.css" rel="stylesheet" />';




									var win = window.open("","imagerHtmlOut");
									win.document.write(style);
								    win.document.write(htmlOut);
								    win.document.title = "PSR HTML Report";

									/* var dWin = new Ext.Window({
											// layout: 'fit',
											title:  "Page Selector",
											layout: 'fit',
											html:htmlOut,
											width: 900,
											height: 600,
											scrollable: true,
											closable: true,
											resizable: true,
											modal: true
										});
									dWin.show();*/
	 						}
	 					});

         var bH = Ext.getBody().getViewSize().height - 300
	     var gridPanel = new Ext.grid.GridPanel({
	 		 header:{
	 				titlePosition: 0,
	 				items: headerButtons
	 		 },
	 		 title: "Imaged Page View",
	 		 height: bH,
	         store: gridStore,
	         width:"100%",
	         id: "imagerMacroTopPageGridId",
	         columns: listColumns,
	         frame: false,
	         collapsible: true,
	         collapsed: false,
	         selModel: 'rowmodel',
 	 		 plugins: ['gridfilters',{
	 			ptype: 'cellediting',
	 			clicksToEdit: 1
	         }]
	     });
	     var tElement = document.getElementById("imagerDivTopId");

	     gridPanel.render(tElement);
		gridPanel.getEl().on('contextmenu', function(e) {
			e.preventDefault();
			gridMenu.showAt(e.clientX+window.pageXOffset,e.clientY+window.pageYOffset);
		});
}

var imagerMacroInitBottomExt = function(inA)
{

   var tFields = [];
   var listColumns = [];

	tFields.push({name: "id", type: 'string'});
	listColumns.push({
			header: "id",
			sortable: true,
			hidden: true,
			width: 20,
			dataIndex: "id",
			filter: {
				type: 'string'
			}
		});

   tFields.push({name: 'chkbx', type: 'boolean'});
	listColumns.push({
			header: "<input type='checkbox' onclick='imagerMacroHeaderBottomChecked(this);'>",
			sortable: false,
			hidden: false,
			xtype: 'checkcolumn',
			centered:true,
			width: 50,
			dataIndex: 'chkbx',
			listeners: {
				checkchange: function(n,o,f)
				{
					null;
				}
			}
	});

	tFields.push({name: "title", type: 'string'});
	listColumns.push({
			header: "Title",
			sortable: true,
			hidden: false,
			width: '40%',
			dataIndex: "title",
			filter: {
				type: 'string'
			}
		});
	tFields.push({name: "space", type: 'string'});
	listColumns.push({
			header: "Space",
			sortable: true,
			hidden: false,
			width: '27%',
			dataIndex: "space",
			filter: {
				type: 'string'
			}
		});
	tFields.push({name: "sourcePageId", type: 'string'});
	listColumns.push({
			header: "SourceId",
			sortable: true,
			hidden: true,
			width: 20,
			dataIndex: "sourcePageId",
			filter: {
				type: 'string'
			}
		});

	tFields.push({name: "psrPageId", type: 'string'});
	listColumns.push({
			header: "psrPageId",
			sortable: true,
			hidden: true,
			width: 20,
			dataIndex: "psrPageId",
			filter: {
				type: 'string'
			}
		});

	tFields.push({name: "targetParentPageId", type: 'string'});
	listColumns.push({
			header: "ParentId",
			sortable: true,
			hidden: true,
			width: 20,
			dataIndex: "targetParentPageId",
			filter: {
				type: 'string'
			}
		});

	tFields.push({name: "versions", type: 'number'});
	listColumns.push({
			header: "Versions",
			sortable: true,
			hidden: false,
			format: "0,000",
			xtype: 'numbercolumn',
			width: '10%',
			dataIndex: "versions",
			filter: {
				type: 'number'
			}
		});


	tFields.push({name: "lastUpdated", type: 'date'});
	listColumns.push({
			header: "Last Updated",
			sortable: true,
			hidden: false,
			//xtype: 'datecolumn',
			renderer: function(inVal){ return moment(inVal).format('M/D/YYYY HH:mm');},
			width: '15%',
			dataIndex: "lastUpdated",
			filter: {
				type: 'date'
			}
		});

		 Ext.define("imagerMacroBottomDataModel", {
			 extend: 'Ext.data.Model',
			 fields: tFields
		 });

	     var gridStore = new Ext.data.Store({
	         model: "imagerMacroBottomDataModel"
	     });


	 	var headerButtons =[];
	 		/*headerButtons.push({
	 						xtype:'button',
	 						style: "background:transparent;border:0px",
	 						text: 'Save',
	 						scope: this,
	 						handler: function(){
	 							 //create record...
	 							 imagerSaveSettings();
	 						}
	 					});*/

	     var gridMenu = new Ext.menu.Menu({ items:
		[
			    { text: 'Create Version of Selected', handler: function()  {
					var selection = gridPanel.getSelection();
					var sourceId = selection[0].data.sourcePageId;
					var targetId = selection[0].data.targetParentPageId;
					var sourceTarget = selection[0].data.title;

					/*var targetParent = imagerMacroGetPageAndChildren(targetId);
					if(!targetParent)
					{
						Ext.Msg.alert("Error","Unable to acquire the children of the parent page");
						return;
					}
					//find the targetId from the target parent.
					var lTarget = "initialize";
					targetParent.children.page.results.forEach(function(p)
					{
						if(p.title == sourceTarget + " (PSR)") lTarget = p.id;
					});
					*/
					var lTarget = selection[0].data.psrPageId;
					if(!lTarget) lTarget = "initialize";
					var res = imagerMacroCopyPage(sourceId, lTarget, Confluence.getContentId());
					if(typeof res != "string") imagerMacroReloadData();
					//Ext.Msg.alert("info",JSON.stringify(res));
					//verify and update...
				} },
			    //{ text: 'Save Entries', handler: function()  {
				//			imagerSaveSettings();
				//} },
				{ text: 'Delete Selection (Full)', handler: function()  {

					    var deleteRec = function()
					    {
							var selection = gridPanel.getSelection();
							var targetId = selection[0].data.targetParentPageId;
							var sourceTarget = selection[0].data.title;
							/*var targetParent = imagerMacroGetPageAndChildren(targetId);
							if(!targetParent)
							{
								Ext.Msg.alert("Error","Unable to acquire the children of the parent page");
								return;
							}
							var lTarget = "initialize";
							targetParent.children.page.results.forEach(function(p)
							{
								if(p.title == sourceTarget + " (PSR)") lTarget = p.id;
							});*/
							var lTarget =selection[0].data.psrPageId;
							if(!lTarget)
							{
								Ext.Msg.alert("Error","Unable to find the child page id.");
								return;
							}
							imagerMacroDeletePageById(lTarget);
							gridStore.remove(selection);
							imagerSaveSettings();
							imagerMacroReloadData();
						}

						Ext.Msg.show({
						    title: "Warning",
						    message: "This will remove this entry and delete the underlying pages, are you sure",
						    buttons: Ext.Msg.OKCANCEL,
						    icon: Ext.Msg.QUESTION,
						    fn: function(btn) {
						        if (btn === 'ok') {
						            deleteRec();
								}
						    }
    					});
				} }

		]});

        var buttons = [];
        buttons.push(
			{ text: 'Delete Checked', style: "background:transparent;border:0px", handler: function()  {

								     var notDone=true;
								     var lData = gridStore.getData();
								     while(notDone)
								     {
										notDone=false;
										lData.items.forEach(function(r)
										{
											var cb = r.get('chkbx');
											if(cb)
											{
												gridStore.remove(r);
												notDone=true;
											}
										});
									 }
									 imagerSaveSettings();
									imagerMacroReloadData();
				} }
			);

 			buttons.push({ text: 'Create Versions of Checked', style: "background:transparent;border:0px", handler: function()  {
					var selection = gridPanel.getStore().getData();
	 		        var lData = gridStore.getData();
					lData.items.forEach(function(r)
					{
						var cb = r.get('chkbx');
						if(cb)
						{
							var sourceId = r.data.sourcePageId;
							var targetId = r.data.targetParentPageId;
							var sourceTarget = r.data.title;
							/*var targetParent = imagerMacroGetPageAndChildren(targetId);
							if(!targetParent)
							{
								Ext.Msg.alert("Error","Unable to acquire the children of the parent page");
								return;
							}
							//find the targetId from the target parent.
							var lTarget = "initialize";
							targetParent.children.page.results.forEach(function(p)
							{
								if(p.title == sourceTarget + " (PSR)") lTarget = p.id;
							});*/
							var lTarget = r.data.psrPageId;
							if(!lTarget) lTarget = "initialize";
							var res = imagerMacroCopyPage(sourceId, lTarget, Confluence.getContentId());

							if(typeof res=="string") console.log(res);
							  else  console.log(JSON.stringify(res));
						}
					});
					imagerMacroReloadData();

				} });

			buttons.push({ text: 'Add Page', style: "background:transparent;border:0px", handler: function()  {
							var addRowFunc = function(page)
							{
							  var rec = Ext.create(gridPanel.store.model);
							  rec.data.id =Ext.id();
								rec.data.title= page.title;
								rec.data.rawtitle= page.title;
								rec.data.targetParentPageId=Confluence.getContentId();
								rec.data.sourcePageId=page.pageId;
								rec.data.space=page.space;
								gridStore.insert(0, rec);
								imagerSaveSettings();

								//create one image here....but only it it doesn't EXIST....
								//save the page tree thing as a global var, then use here....
								var targetParent = imagerMacroGetPageAndChildren(rec.data.targetParentPageId);
								if(!targetParent)
								{
									Ext.Msg.alert("Error","Unable to acquire the children of the parent page");
									return;
								}
								//find the targetId from the target parent.
								var lTarget = null;
								targetParent.children.page.results.forEach(function(p)
								{
									if(p.title == rec.data.title + " (PSR)") lTarget = p.id;
								});

								//loop child page histories...
								if(!lTarget) var res = imagerMacroCopyPage(page.pageId, "initialize", Confluence.getContentId());

								if(typeof res=="string") console.log(res);
								  else  console.log(JSON.stringify(res));

								imagerMacroReloadData();
							}
	 						    imagerMacroPagePicker(addRowFunc);
				} });


	     var gridPanel = new Ext.grid.GridPanel({
	 		 title: "Imaged Page Settings",
	 		 height: 300,
	 		 header:{
	 				titlePosition: 0,
	 				items: headerButtons
	 		},
	         store: gridStore,
	         width:"100%",
	         id: "imagerMacroBottomPageGridId",
	         columns: listColumns,
	         frame: false,
	         collapsible: true,
	         collapsed: true,
	         selModel: 'rowmodel',
	         buttons: buttons,
 	 		 plugins: ['gridfilters',{
	 			ptype: 'cellediting',
	 			clicksToEdit: 1
	         }]
	     });
	     var tElement = document.getElementById("imagerDivTopId");

	     gridPanel.render(tElement);
		 gridPanel.getEl().on('contextmenu', function(e) {
			e.preventDefault();
			gridMenu.showAt(e.clientX+window.pageXOffset,e.clientY+window.pageYOffset);
		});
}

var imagerMacroLoadPageGrid=function(inData)
{

    var pageDetail = imagerMacroGetPageAndChildren(Confluence.getContentId());
	//var pageDetail = imagerMacroGetPageAndChildren(Confluence.getContentId());

	inData.forEach(function(r)
	{
		r.id = r.sourcePageId;
		r.lastUpdated = null;
		r.rawtitle = r.title;
		r.versions = null;
		r.psrPageId = null;
		pageDetail.children.page.results.forEach(function(p)
		{
			if(p.title== r.title + " (PSR)" )
			{
				r.lastUpdated = moment(p.version.when).format('M/D/YYYY HH:mm');
				r.versions = p.version.number;
				r.psrPageId = p.id;
			}
		});
        r.title = "<a href='/pages/viewpage.action?pageId="+r.sourcePageId+"' target='_blank'>"+r.rawtitle+" (Source)</a>";
	});
	var grid = Ext.getCmp("imagerMacroBottomPageGridId");
	grid.getStore().loadData(inData);

    var topDatea = JSON.parse(JSON.stringify(inData))
    var psrPageId="xxx";
	topDatea.forEach(function(r)
	{
		r.title = r.rawtitle;
		r.id = r.sourcePageId;
		r.rawtitle = r.title;
		r.lastUpdated = null;
		r.versions = null;
		r.psrPageId = null;
		psrPageId='xxx';
		pageDetail.children.page.results.forEach(function(p)
		{
			if(p.title== r.title + " (PSR)" )
			{
				r.lastUpdated = moment(p.version.when).format('M/D/YYYY HH:mm');
				r.versions = p.version.number;
				psrPageId=p.id;;
				r.psrPageId = p.id;
			}
		});
		r.title = "<a href='/pages/viewpage.action?pageId="+psrPageId+"' target='_blank'>"+r.title+" (PSR)</a>";
	});
	var grid2 = Ext.getCmp("imagerMacroTopPageGridId");
	grid2.getStore().loadData(topDatea);
}

var imagerGetGridValues = function ()
{

	var grid = Ext.getCmp("imagerMacroBottomPageGridId");
    var gridData = grid.getStore().getData();
    var dataArray = gridData.items.map(function(r){r.data.title=r.data.rawtitle; return r.data;});

	return dataArray;
}

var imagerMacroHeaderTopChecked = function(cb)
{
	var grid = Ext.getCmp("imagerMacroTopPageGridId");
	var gridData = grid.getStore().getData();
	var c = cb.checked;
	gridData.items.forEach(function(r)
	{
		r.set('chkbx',c);
	});
}
var imagerMacroHeaderBottomChecked = function(cb)
{
	var grid = Ext.getCmp("imagerMacroBottomPageGridId");
	var gridData = grid.getStore().getData();
	var c = cb.checked;
	gridData.items.forEach(function(r)
	{
		r.set('chkbx',c);
	});
}
var imagerMacroCommitSave = function()
{
	var grid = Ext.getCmp("imagerMacroBottomPageGridId");
	var gridData = grid.getStore().getData();
	gridData.items.forEach(function(r){r.commit()});
}

var imagerSaveSettings = function()
{
	sOut=imagerGetGridValues();
	imagerMacroPostSettings(sOut);
	//Ext.Msg.alert("Info","Saved");
}


/**************page picker *********************/

var imagerMacroPagePicker = function(inFunction)
{


   var tFields = [];
   var listColumns = [];

	tFields.push({name: "pageId", type: 'string'});
	listColumns.push({
			header: "ID",
			sortable: true,
			hidden: true,
			width: '0%',
			dataIndex: "pageId",
			filter: {
				type: 'string'
			}
		});

	tFields.push({name: "title", type: 'string'});
	listColumns.push({
			header: "Title",
			sortable: true,
			hidden: false,
			width: '74%',
			dataIndex: "title",
			filter: {
				type: 'string'
			}
		});

	tFields.push({name: "space", type: 'string'});
	listColumns.push({
			header: "Space",
			sortable: true,
			hidden: false,
			width: '24%',
			dataIndex: "space",
			filter: {
				type: 'list'
			}
		});


    if(!Ext.ClassManager.isCreated("imagerMacroPagePickerModel"))
    {
		 Ext.define("imagerMacroPagePickerModel", {
			 extend: 'Ext.data.Model',
			 fields: tFields
		 });
    }


	     var gridStore = new Ext.data.Store({
	        model: "imagerMacroPagePickerModel",
	        pageSize: 100,
        	proxy: {
			        type: 'ajax',
			        url: '/rest/api/content/search?cql=type=page&expand=space',
			        reader: {
			            type: 'json',
			            rootProperty: 'results',
			            totalProperty: 'total',
						transform: function(data) {
								// do some manipulation of the raw data object
								 data.results = data.results.map(function(i){
											var retObj ={};
											retObj.pageId= i.id;
											retObj.title = i.title;
											retObj.space = i.space.name;
											return retObj;
										});
								return data;
			            }
					}
        	},
        	listeners: {"beforeload":function (store, operation, eOpts ) {

				operation._proxy.extraParams["maxResults"]= operation._limit;
				operation._proxy.extraParams["startAt"]= operation._start;
			}}
        });
        gridStore.load({
					params: {
						limit: 100,
						start: 0,
						// specify params for the first page load if using paging
						//startAt: 0,
						//maxResults: 2,
					}
				});


	     var gridPanel = new Ext.grid.GridPanel({
	 		 height: 300,
	         store: gridStore,
	         width:"100%",
	         //layout: 'fit',
	         id: "imagerMacroPageFinderGrid",
	         columns: listColumns,
	         frame: false,
	         //bbar: {    xtype: 'pagingtoolbar',
			 //	        displayInfo: true},
	         selModel: 'rowmodel',
 	 		 plugins: ['gridfilters'],
			listeners: {
				'beforeitemdblclick': function(selMod, record, something ){

					var nVal = {"pageId":record.data.pageId,"title":record.data.title,"space":record.data.space};
					dWin.close();
					inFunction(nVal);
				}
			}
	     });



	 var dWin = new Ext.Window({
	        // layout: 'fit',
	        title:  "Page Selector",
	        laout: 'vbox',
	        width: 800,
	        height: 400,
	        scrollable: "vertical",
	        closable: true,
	        items: [{
					xtype: 'textfield',
					labelAlign: 'left',
					fieldLabel: 'Search',
					labelWidth: 50,
					margin: '8 0 8 20',
					width:530,
					value: "",
					listeners: {
						change: function(f,n,o){
							   //filter
							}
						}
					},
					gridPanel],
	        modal: true
	    });
    dWin.show();
    var bH = Ext.getBody().getViewSize().height - 300;
    dWin.setY(bH);

}

var imagerMacroGetPageAndChildren = function(sourcePageId)
{
    var retData = null;
		jQuery.ajax({
			async: false,
			type: 'GET',
		    contentType: 'application/json',
			url: '/rest/api/content/search?cql=type=page%20and%20id='+sourcePageId+'&expand=children.page.version',
			timeout: 60000,
			success: function(data) {
				retData = data.results[0];
			},
			error: function(e) {
				if(e.responseText)
				{
					retData = null;
				}
				else
				{
					retData = null;
				}
			}
		});
		if(!retData)
		{
			Ext.Msg.alert("Error","Error performing page copy")
			return;
		}
		return retData;
}
var imagerMacroGetPageById = function(sourcePageId)
{
    var retData = null;
		jQuery.ajax({
			async: false,
			type: 'GET',
		    contentType: 'application/json',
			url: '/rest/api/content/'+sourcePageId,
			timeout: 60000,
			success: function(data) {
				retData = data.results[0];
			},
			error: function(e) {
				if(e.responseText)
				{
					retData = null;
				}
				else
				{
					retData = null;
				}
			}
		});
		return retData;
}
var imagerMacroGetPageVersionsById = function(sourcePageId)
{
    var retData = null;
		jQuery.ajax({
			async: false,
			type: 'GET',
		    contentType: 'application/json',
			url: '/rest/experimental/content/'+sourcePageId+ '/version',
			timeout: 60000,
			success: function(data) {
				retData = data.results;
			},
			error: function(e) {
				if(e.responseText)
				{
					retData = null;
				}
				else
				{
					retData = null;
				}
			}
		});
		return retData;
}
var imagerMacroGetPageStyledView = function(sourcePageId)
{
    var retData = null;
		jQuery.ajax({
			async: false,
			type: 'GET',
		    contentType: 'application/json',
			url: '/rest/api/content/'+sourcePageId+'?expand=body.styled_view',
			timeout: 60000,
			success: function(data) {
				retData = data;
			},
			error: function(e) {
				if(e.responseText)
				{
					retData = null;
				}
				else
				{
					retData = null;
				}
			}
		});
		return retData;
}
var imagerMacroGetPageView = function(sourcePageId)
{
    var retData = null;
		jQuery.ajax({
			async: false,
			type: 'GET',
		    contentType: 'application/json',
			url: '/rest/api/content/'+sourcePageId+'?expand=body.view',
			timeout: 60000,
			success: function(data) {
				retData = data;
			},
			error: function(e) {
				if(e.responseText)
				{
					retData = null;
				}
				else
				{
					retData = null;
				}
			}
		});
		return retData;
}

var imagerMacroGetPageVersionRest = function(sourcePageId, versionNumber)
{
    var retData = null;
		jQuery.ajax({
			async: false,
			type: 'GET',
		    contentType: 'application/json',
			url: '/rest/experimental/content/'+sourcePageId+'/version/'+versionNumber,
			timeout: 60000,
			success: function(data) {
				retData = data;
			},
			error: function(e) {
				if(e.responseText)
				{
					retData = null;
				}
				else
				{
					retData = null;
				}
			}
		});
		return retData;
}



var imagerMacroDeletePageById = function(sourcePageId)
{
    var retData = null;
		jQuery.ajax({
			async: false,
			type: 'DELETE',
		    contentType: 'application/json',
			url: '/rest/api/content/'+sourcePageId,
			timeout: 60000,
			success: function(data) {
				retData = true;
			},
			error: function(e) {
				retData=false;
			}
		});
		return retData;
}



