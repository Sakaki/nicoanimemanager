jQuery(document).ready( function() {

function api(command) {
    var d = new $.Deferred;
    $.getJSON("/api/"+command, function(data, status, xhr) {d.resolve(data);});
    return d.promise();
}

function rev_recording(event) {
    channel = event.data.ch;
    if($('#cbox_'+channel).is(":checked")) {
	$.get("/api/addrec?channel="+channel);
    } else {
	$.get("/api/delrec?channel="+channel);
    }
}

var Panel = (function() {
    var Panel = function(panelhtml, conffunc, menulabel) {
	this.panelhtml = panelhtml;
	this.conffunc = conffunc;
	$("#current").text("> "+menulabel);
    };

    var p = Panel.prototype;

    p.draw = function() {
	console.log(this.panelhtml);
	this.loadBase($("#plate"), this.panelhtml).then(this.conffunc);
    };

    p.loadBase = function(plate, src) {
	var d = new $.Deferred;
	plate.load(src, null, function() {d.resolve();});
	return d.promise();
    };

    return Panel;
})();

function allAnimes() {
    $("#refresh").click(function(){
        $("#refresh").text("更新しています");
	api("refreshanimelst").then(allPanel.draw.bind(allPanel));
    });
    $.when(api("getallrecs"), api("getanimelst"))
    .then(function(allrecs_data, animelst_data){
	$(animelst_data.allanimes).each(function(){
	    var channel = this.channel;
	    var link = this.link;
	    var title = this.title;
	    var cbox = "#cbox_"+channel;
	    var weekday = this.weekday;
	    $('<tr><td><input type="checkbox" class="center" id="cbox_'+channel+'" /></td><td><a href="' + link + '" target="_blank">' + title + '</a></td></tr>').appendTo("#allanimes_"+weekday);
	    if($.inArray(channel, allrecs_data.result) != -1) {
		$('#cbox_'+channel).attr("checked", true);
	    }
	    $('#cbox_'+channel).click({ch : channel}, rev_recording);
	});
    });
}

function reservation() {
    $.when(api("getallrecs"), api("getanimelst"))
    .then(function(allrecs_data, animelst_data) {
        $(animelst_data.allanimes).each(function(){
	    var channel = this.channel;
	    var link = this.link;
	    var title = this.title;
	    var cbox = "#cbox_"+channel;
	    if($.inArray(channel, allrecs_data.result) == -1) {
                return true;
	    }
	    $('<tr><td><input type="checkbox" class="center" id="cbox_'+channel+'" checked /></td><td>' + title +
	      '</td><td><a href="' + link + '">' + link + '</a>' +
	      '</td></tr>').appendTo("#allanimes_table");
	    $('#cbox_'+channel).click({ch : channel}, rev_recording);
	});
    });
}

function recorded() {
    $("#refresh").click(function(){
	$("#refresh").text("更新しています");
	api("updatechinfo").then(recPanel.draw.bind(recPanel));
    });
    $("#dlall").click(function(){
	$("#dlall").text("ダウンロード中");
	api("dlallanimes")
        .then(function() {
	    return dlWatcher();
	}).then(function() {
	    recPanel.draw.bind(recPanel);
	});
    });
    api("getrecorded")
    .then(function(reclst) {
	$(reclst.titles).each(function(){
	    var channel = this.channel;
	    var title = this.title;
	    $('<button class="pure-button button-title" id="title_' + channel + '">' + title + '</button><button class="pure-button button-del-channel" id="delch_' + channel + '">削除</button>').appendTo("#titles");
	    $('#title_' + channel).click(function() {
		detail(title);
	    });
	    $('#delch_' + channel).click(function() {
		if (confirm("本当に " + title + " を削除しますか？") == true) {
		    api("delanime?title=" + title + "&channel=" + channel).then(recPanel.draw.bind(recPanel));
		}
	    });
	});
    });
}

function findStoryByIdx(storylst, idx) {
    var res;
    $(storylst).each(function(si) {
	if(this.idx == idx) {
	    res = JSON.parse(JSON.stringify(this));
	    return false;
	}
    });
    return res;
}

function dlWatcher() {
    var d = new $.Deferred;
    var watcher = setInterval(function(){
	api("dlstate")
        .then(function(res) {
            if(res.result == 0) {
                clearInterval(watcher);
                d.resolve();
            }
        });
    },3000);
    return d.promise();
}

function setRecordState(title, tgtstory, recState) {
    var vid = tgtstory.vid;
    var link = tgtstory.link;
    var vname = tgtstory.title;

    if(recState == 0) {
        $('#state_' + vid).text("録画不可");
        $('#action_' + vid).html('<a href="' + link + '" target="_blank">動画ページ</a>');
    } else if(recState == 1) {
        $('#state_' + vid).text("録画可");
        $('#action_' + vid).html('<button class="pure-button" id="dl_' + vid + '">ダウンロード</button>');
	$('#dl_' + vid).click(function(){
	    api("downloadvideo?title=" + title + "&vname=" + vname + "&vid=" + vid)
            .then(function(apires) {
		if(apires.result == 1) {
                    alert("他のダウンロードが実行中なのでダウンロードできません。");
                } else {
                    $('#dl_' + vid).text('ダウンロード中');
                    $('#dl_' + vid).attr("class", "pure-button pure-button-disabled");
		    dlWatcher().then(function() {setRecordState(title, tgtstory, 2);});
                }
	    });
	});
    } else if(recState == 2) {
        $('#state_' + vid).text("録画済");
        $('#action_' + vid).html('<button class="pure-button" id="watch_' + vid + '">観る</button><button class="delbutton pure-button" id="delstory_' + vid + '">削除</button>');
        $('#watch_' + vid).click(function (){
            $("body").append('<div id="modal-overlay"></div>');
            centeringModalSyncer();
            $("#modal-overlay").fadeIn("slow");
            $("#modal-content").fadeIn("slow");
            $("#modal-overlay,#modal-close").unbind().click(function(){
                player.pause();
                $("#modal-content,#modal-overlay").fadeOut("slow",function(){
                    $('#modal-overlay').remove();
                });
            });
            player.setSrc("/webui/video/" + title + "/" + vname + ".flv");
        });
        $('#delstory_' + vid).click(function (){
            if (confirm("本当に " + vname + " を削除しますか？") == true) {
		api("delstory?title=" + title + "&vname=" + vname).then(function(){detail(title)});
            }
        });
    } else if(recState == 3) {
        $('#state_' + vid).text("録画中");
        $('#action_' + vid).html('<button class="pure-button pure-button-disabled">ダウンロード中</button>');
    }
}

function detail(title) {
    $.ajaxSetup({async : false});
    recPanel.loadBase($('#rec_detail'), 'recorded-detail.html')
    .then(function() {
        return api("getdetail?title="+title);
    }).then(function(storyData) {
        $(storyData.stories).each(function(i){
	    var story = findStoryByIdx(storyData.stories, i);
            var vname = story.title;
            var vid = story.vid;
	    var recState;
            api("getvideostate?title=" + title + "&vname=" + vname)
            .then(function(recStateData) {
		recState = recStateData.result;
                return $('<tr><td>' + vname + '</td><td id="state_' + vid + '">' +
			 '</td><td class="actionbox" id="action_' + vid + '">' +
			 '</td></tr>').appendTo("#stories");
            }).then(function() {
		console.log(recState);
                setRecordState(title, story, recState);
	    });
	    i = i + 1;
        });
    });
    $.ajaxSetup({async : true});
}

function config() {
    api("readconf")
    .then(function(confData) {
	console.log(JSON.stringify(confData.result));
	$('#confarea').val(JSON.stringify(confData.result, null, "    "));
    });
    $("#saveconf").click(function() {
	var confStr = $('#confarea').val();
	confStr = JSON.stringify(JSON.parse(confStr));
	console.log(confStr);
	api("writeconf?conf=" + confStr);
    });
    $("#resetconf").click(function() {
        if (confirm("本当にリセットしますか？") == true) {
	    api("resetconf").then(confPanel.draw.bind(confPanel));
	}
    });
}

function centeringModalSyncer(){
    var w = $(window).width();
    var h = $(window).height();
    var cw = $("#modal-content").outerWidth(true);
    var ch = $("#modal-content").outerHeight(true);
    $("#modal-content").css({"left": ((w - cw)/2) + "px","top": ((h - ch)/2) + "px"});
}

var player = new MediaElementPlayer('#player', {
    features: ['playpause', 'progress', 'current', 'duration', 'volume', 'fullscreen']
});
$(window).resize(centeringModalSyncer);

var allPanel = new Panel("allanimes.html", allAnimes, "アニメ一覧");
var reservePanel = new Panel("recording.html", reservation, "予約");
var recPanel = new Panel("recorded.html", recorded, "録画済み");
var confPanel = new Panel("config.html", config, "設定");

$("#allanimes").click(allPanel.draw.bind(allPanel));
$("#recording").click(reservePanel.draw.bind(reservePanel));
$("#recorded").click(recPanel.draw.bind(recPanel));
$("#config").click(confPanel.draw.bind(confPanel));

});
