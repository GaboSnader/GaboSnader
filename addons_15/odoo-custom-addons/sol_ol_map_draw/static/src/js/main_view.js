odoo.define('sol_ol_map_draw.SolverMapOL', function (require) {
"use strict";

var AbstractController = require('web.BasicController');
var AbstractModel = require('web.BasicModel');
var AbstractRenderer = require('web.BasicRenderer');
var AbstractView = require('web.AbstractView');

var BasicView = require('web.BasicView');
var BasicController = require('web.BasicController');
var BasicModel = require('web.BasicModel');
var BasicRenderer = require('web.BasicRenderer');

var viewRegistry = require('web.view_registry');
var solmap_common = require('sol_ol_map_draw.solmap_common');
var core = require("web.core");
var qweb = core.qweb;
var session = require('web.session');
var widgetRegistry = require('web.widget_registry');
var field_utils = require('web.field_utils');
var rpc = require('web.rpc');

var SolverMapController = BasicController.extend({});

var SolverMapRenderer = BasicRenderer.extend({
    className: "o_sol_map_ol_view",

    init: function (parent, state, params) {
        this._super.apply(this, arguments);
        this.longitude=params.longitude;
        this.latitude=params.latitude;
        this.geofield= params.geofield;
        this.mapTemplate = params.mapTemplate;
        this.viewInfo = params.viewInfo;
        this.viewFieldsChildrenAttrs = params.arch.children;
        this.viewAttrsArray = [];
        this.viewAttrsWidget = [];
        this.overlayPopup = null;
        this.container = null;
        this.popupContent = null; //used
        //this.popupCloser = null;
        this.isPopUpOpen = 0;
        this.overlayContent={};
        console.log('init');
        this._getFieldAttesArray();
        this.isInDOM=false;

    },

     _getFieldAttesArray: function(){
        var self = this;
        _.each(this.viewFieldsChildrenAttrs, function (item) {
             if(item.attrs.projection){
                self.viewAttrsArray[item.attrs.name]=item.attrs;
             }else if(item.attrs.widget){
                self.viewAttrsWidget[item.attrs.name]=item;
             }
        });
    },
    _getFieldWidget: function(name){
        return this.viewAttrsWidget[name];
    },
    _getRelationalFieldProjection: function(name){
        return this.viewAttrsArray[name].projection;
    },

    _getKeys: function(object){

        return Object.keys(object);
    },

    _loadOverlayContentTemplate : function(model, callback){
        var self = this;
        rpc.query({
            model: 'sol.map.manage.overlay',
            method: 'search_read',
            fields: ['name','overlay_template'],
            domain: [['is_default', '=', true],['model_name', '=', model]],
            limit: 1,
        })
        .then(function (result) {
            if (result.length>0){
                qweb.add_template(result[0].overlay_template);
                callback(result[0]);
            }
        }).catch(function (e) {
            console.log('_loadOverlayContentTemplate',e);
        });
    },

    updateState: function (state, params) {
        this._super.apply(this, arguments);
        if(this.map){
            this._renderMarkers();
        }
        return $.when();
    },

    on_attach_callback: function () {
        if (this.isInDOM) {
            var self = this;
            this._renderMap();
            if(this.map){
                this._renderMarkers();
                this._renderPopupOverlay();
                if(this.geofield){
                    this._createSearchControl();
                }
                this._loadOverlayContentTemplate(this.state.model,function(data){
                    self.overlayContent = data;
                });
            }
        }
        return this._super();
    },

    _renderView: function () {
        console.log('_renderView');
        this._onPopUpCloserClick();
        if(!this.isInDOM){
            this.isInDOM = true;
            if (this.mapTemplate){
                this.$el.append(qweb.render(this.mapTemplate.name));
                return this._super();
            }
            this.$el.append(qweb.render('Empty'));
        }
        return this._super();
    },

	_mapSetCenter : function(coord){
        if (this.map) {
            this.map.getView().setCenter(coord);
        }
	},

    renderExtMarkers: function(){
        this.placemark = new ol.Overlay.Placemark({
              position:  [0, 0],
              stopEvent: false
            });
            this.map.addOverlay(this.placemark);
    },

    _renderMap: function () {
        if (!this.map) {
              this.map = new ol.Map({
              layers: [
                new ol.layer.Tile({
                  source: new ol.source.OSM(),
                }) ],
              target: 'olmap',
              view: new ol.View({
                center: ol.proj.fromLonLat([0,0]),
                zoom: 5,
              }),
            });
        }
        return this.map;
    },

    _renderMarkers: function () {
       var self = this;
       if (!this.icon_layer) {
            this.icon_layer = new ol.layer.Vector({
                source: new ol.source.Vector({
                features: [],
                })
            });
       this.icon_layer.set('name', 'markers');
       this.map.addLayer(this.icon_layer);
       this.map.on('click',self._onMarkerClick.bind(self));

       }else if (this.icon_layer.getSource().getFeatures().length > 0){
            this.icon_layer.getSource().clear();
       }
        var iconFeatures = [];
        var iconStyle = new ol.style.Style({
            image: new ol.style.Icon({
                anchor: [0.3, 23],
                color: '#23424C',
                anchorXUnits: 'fraction',
                anchorYUnits: 'pixels',
                imgSize : [32,32],
                src: '/sol_ol_map_draw/static/imgs/map-marker.png',
            }),
      });
      var _longitude=this.longitude;
      var _latitude=this.latitude;

       _.each(this.state.data, function (item) {
            if(!item.data){
                return;
            }
           if( parseInt(item.data[_longitude]) != 0 && parseInt(item.data[_latitude]) != 0){
                var Feature = new ol.Feature({
                    geometry: new ol.geom.Point(
                    ol.proj.transform([item.data[_longitude], item.data[_latitude]],'EPSG:4326', 'EPSG:3857')
                    ),
                    name: item.data['name'],
                    id: item.data['id'],
                 });
                var _relationalFieldsObject = {};
                var _dataFieldsObject = {};
                _.each(Object.keys(self.viewInfo.viewFields), function (viewItem) {
                    var _data = item.data[viewItem];
                    var _flag = 0;
                    var _fieldType = '';
                    if (typeof _data === 'string'){
                        if (_data.trim().length >0)
                            _flag=1;
                    }else if(typeof _data === 'number'){
                        if (_data >0)
                            _flag=1;
                        if(self.viewInfo.viewFields[viewItem].type==='monetary'){
                            _data = field_utils.format.monetary(_data, self._getFieldWidget(viewItem));
                        }
                    }else if(typeof _data === 'object'){
                        if (_data !== null){
                            _flag=0;
                            if(_data.type === 'list' && _data.res_ids.length>0){//one2many
                                var projection = self._getRelationalFieldProjection(viewItem);
                                if (!projection || projection.length===0){
                                    projection = "'id','name','display_name'";
                                }
                                rpc.query({
                                    model: self.viewInfo.viewFields[viewItem].relation,
                                    method: 'search_read',
                                    fields: projection.split(","),
                                    domain: [['id', 'in', item.data[viewItem].res_ids]],
                                })
                                .then(function (result) {
                                    var RelationalFields = {
                                        title : self.viewInfo.viewFields[viewItem].string,
                                        model : self.viewInfo.viewFields[viewItem].relation,
                                        ids : item.data[viewItem].res_ids,
                                    };
                                    RelationalFields['data'] = result;
                                    _relationalFieldsObject[viewItem]=RelationalFields;
                                }).catch(function (e) {
                                    console.log('render marker',e);
                                });
                            }else if(_data.type === 'record' && _data.res_id > 0){ //many2one
                                _flag=1;
                                _data = _data.data;
                            }
                        }
                    }
                    if (_flag >0){
                        var dataFields = {
                                title : self.viewInfo.viewFields[viewItem].string,
                                data : _data,
                        };
                        if (viewItem.indexOf('image') !== -1 ){ //==='image_1920'
                            dataFields['src'] =window.location.origin + '/web/image?model='+self.state.model+'&id='+item.res_id+'&field='+viewItem;
                        }
                        _dataFieldsObject[viewItem] = dataFields;
                    }
                });
                _dataFieldsObject['res_id'] = item.res_id;
                Feature.set('RelationalFields',_relationalFieldsObject);
                Feature.set('DataFields',_dataFieldsObject);
                Feature.setStyle(iconStyle);
                iconFeatures.push(Feature);
            }
       });
        if(iconFeatures.length>0){
            var coord = ol.extent.getCenter(iconFeatures[0].getGeometry().getExtent());
            this._mapSetCenter(coord);
        }
       this.icon_layer.getSource().addFeatures(iconFeatures);
    },

    _onMarkerClick: function (event) {
        if(this.map){
            var _feature =0;
            var self = this;
            var atPixel =false;
            this.map.forEachFeatureAtPixel(event.pixel, function (feature, layer) {
                if(feature.get('noClick')){
                    return;
                }
                _feature = feature.getProperties();
                var coord = ol.extent.getCenter(feature.getGeometry().getExtent());
                self.overlayPopup.setPosition(coord);
                var _template_popup = qweb.render(self.overlayContent.name,{
                                        DataFields : _feature.DataFields,
                                        RelationalFields :_feature.RelationalFields,
                                        Model : self.state.model,
                                        });
                self.popupContent.innerHTML =_template_popup;
                atPixel=true;
            });
            if(atPixel && _feature){
                var $a = self.$('.Relational-Fields-Overlay');
                if ($a.get(0)){
                    $a.click(self._onRelationalFieldsOverlay.bind(self));
                }
                var $DetailButton = self.$('#SolMapDetailModel');
                if ($DetailButton.get(0)){
                    $DetailButton.click(self._onPopUpDetailClick.bind(self));
                }
            }
        }
    },

    _renderPopupOverlay: function () {
        if (this.overlayPopup !== null) {
            return this.overlayPopup;
        }
        var self=this;
        var $container = this.$('.ol-popup');
        var $content = this.$('#popup-content');
        var popupElement= $container.get(0);
        var popupContent =  $content.get(0);
        var overlayPopup = new ol.Overlay({
            element: popupElement,
            autoPan: true,
            autoPanAnimation: {
                duration: 250,
            },
            stopEvent: false,
        });
        this.container = popupElement;
        this.popupContent = popupContent;
        this.overlayPopup = overlayPopup;
        this.map.addOverlay(this.overlayPopup);
        this.$('.ol-popup-closer').click(this._onPopUpCloserClick.bind(this));
        return overlayPopup;
    },

    _onPopUpCloserClick: function (event){
        if (this.overlayPopup !== null) {
            this.overlayPopup.setPosition(undefined);
            this.$('.ol-popup-closer').get(0).blur();
        }
    },

    _onRelationalFieldsOverlay : function(event){
        var id, model;
        id =parseInt(event.target.getAttribute("id"));
        model = event.target.getAttribute("model");
        var action = {
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            res_model: model,
            res_id: id,
        };
        this.do_action(action);
    },

    _onPopUpDetailClick: function (event){
        var id, model;
        id =event.target.getAttribute("res_id");
        model = this.viewInfo.model;
        var action = {
            type: 'ir.actions.act_window',
            views: [[false, 'form']],
            res_model: this.viewInfo.model,
            res_id: parseInt(event.target.getAttribute("res_id")),
        };
        this.do_action(action);
    },

    _createSearchControl: function () {
         var features=[];
         var self = this;
        _.each(this.state.data, function (item) {
            if(!item.data){
                return;
            }
            self._onPopUpCloserClick();
            var _map_form =self.geofield;
            if(item.data[_map_form]){
                var feature_object = new ol.format.GeoJSON().readFeatures(item.data[_map_form]);
                _.each(feature_object, function (feature) {
                    if(feature){
                         if (feature.get('key_word') != '' && feature.get('key_word')){
                            features.push(feature);
                        }
                    }
                });
            }
        });
	    var search = new ol.control.Search(
		{
			getTitle: function(feature) { return feature.name; },
			autocomplete: function (s, cback)
			{
			    var result = [];
				// New search RegExp
				var	rex = new RegExp(s.replace("*","")||"\.*", "i");
				_.each(features, function (feature) {
                    if (rex.test(feature.get('key_word') ))
                        result.push(
                            {
                                name :feature.get('key_word'),
                                geometry : feature.getGeometry(),
                            }
                        );
				});
				return result;
			}
		});
	    this.map.addControl(search);
	    search.clearHistory();
	    self = this;
	    search.on('select', function(e)
		{
		    _.each(self.icon_layer.getSource().getFeatures(), function(feature){
		        if(feature.get('noClick')){
		            self.icon_layer.getSource().removeFeature(feature);
		        }
		    });
		    self.icon_layer.getSource().addFeature(
		        new ol.Feature({
                    geometry:e.search.geometry,
                    name: e.search.name,
                    noClick :true,
                    text: self.map.getView().getZoom() > 12 ? e.search.name : ''
		        })
		     );
		    self.map.getView().animate({
				center: e.search.geometry.getExtent(),
				zoom: 11,
				easing: ol.easing.easeOut
			})
		});
    },

});

var SolverMapModel = BasicModel.extend({});


var SolverMapView = BasicView.extend(solmap_common.SolMapMixin,{
    accesskey: 'g',
    display_name:'sol Map',
    icon: 'fa-map-o',
    config: _.extend({}, BasicView.prototype.config, {
        Model: SolverMapModel,
        Controller: SolverMapController,
        Renderer: SolverMapRenderer,
    }),
    viewType: 'solmap',
    template: 'SolMapView',
    groupable: false,


    init: function (viewInfo, params) {
        this._super.apply(this, arguments);
        this.rendererParams.viewInfo = viewInfo;
        this.rendererParams.latitude = this.arch.attrs.latitude;
        this.rendererParams.longitude = this.arch.attrs.longitude;
        this.rendererParams.geofield = this.arch.attrs.geofield;
        var self = this;
        this._loadOlMapTemplate('sol.map.manage.overlay',function(data){
            self.rendererParams.mapTemplate = data;
        });
        console.log('init view');
    },

    _loadOlMapTemplate : function(model, callback){
        var self = this;
        rpc.query({ //ir.ui.view arch_base  active model priority
            model: 'sol.map.manage.overlay',
            method: 'search_read',
            fields: ['name','overlay_template'],
            domain: [['is_default', '=', true],['model_name', '=', model]],
            limit: 1,
        })
        .then(function (result) {
            if (result.length>0){
                qweb.add_template(result[0].overlay_template);
                callback(result[0]);
            }
        }).catch(function (e) {
            console.log('_loadOlMapTemplate',e);
        });
    },

/*
if (node.tag === 'button') {
    return $td.append(this._renderButton(record, node));
} else if (node.tag === 'widget') {
    return $td.append(this._renderWidget(record, node));
}
*/
});

viewRegistry.add('solmap', SolverMapView);

return SolverMapView;

});


