/* login */
    function test(form, callback)
    {
        if(form.login.value == '' || form.password.value == '' || (form.login.value == '&#208;&#155;&#208;&#190;&#208;&#179;&#208;&#184;&#208;&#189;' && form.password.value == '&#208;&#159;&#208;&#176;&#209;&#128;&#208;&#190;&#208;&#187;&#209;&#140;'))
        {
            _show(_$('qip_login_error'));
            trytofocus(form.login);
            return false;
        }

        disableForm(form, true);

        JsHttpRequest.query(
            window.login_url + '?r=' + Math.random(),
            {
                user : form.login.value,
                host : (
                    (form.host.tagName.toLowerCase() === 'select')
                        ? form.host.options[form.host.selectedIndex].value
                        : form.host.value
                    ),
                pass : form.password.value,
                alien: form.alien.checked,
                time : new Date().getTimezoneOffset()
            },
            function(result, debugMessages)
            {
                if(debugMessages)
                    alert(debugMessages);

                if(result.code == 200)
                {
                    var redirUrl = _$('qip_login_redirect').value;
                    if(redirUrl.length)
                    {
                        if(redirUrl == 'self')
                            window.location.reload();
                        else
                            window.location = redirUrl;
                        return;
                    }

                    hideLoginFrom(1);
                    _hide(_$('qip_login_error'));

                    var jid = form.login.value.toLowerCase().split('@');
                    var username = jid[0], domain = jid[1] || (
                        (form.host.tagName.toLowerCase() === 'select')
                            ? form.host.options[form.host.selectedIndex].value
                            : form.host.value
                        );
                    jid = username + '@' + domain;

                    var username_top  = jid.length <= 25 ? jid : (jid.substr(0, 22) + '...');
                    var username_info = username.length <= 12 ? username : (username.substr(0, 11) + '...');

                    _$('qhu_username').innerHTML = username_top;

                    setClass(_$('qip_head'), 'qip_head_auth');
                    if(_$('q_login_mail'))
                        setClass(_$('q_login_mail'), 'q_login_mail_auth');

                    if(('fn' in result) && _$('qlm_greeting'))
                        _$('qlm_greeting').innerHTML = getDayTime() + (result.fn.length ? (', ' + result.fn) : '');

                    updateOwnCabinet();

                    return;
                }

                var er_msg = _$('qip_login_error');
                if(result.code == 400 && result.login && result.key)
                    er_msg.innerHTML = '&#208;&#163;&#209;&#135;&#208;&#181;&#209;&#130;&#208;&#189;&#208;&#176;&#209;&#143; &#208;&#183;&#208;&#176;&#208;&#191;&#208;&#184;&#209;&#129;&#209;&#140; &#208;&#177;&#209;&#139;&#208;&#187;&#208;&#176; &#209;&#128;&#208;&#176;&#208;&#189;&#208;&#181;&#208;&#181; &#209;&#131;&#208;&#180;&#208;&#176;&#208;&#187;&#208;&#181;&#208;&#189;&#208;&#176;. ' + '&#208;&#146;&#208;&#190;&#209;&#129;&#209;&#129;&#209;&#130;&#208;&#176;&#208;&#189;&#208;&#190;&#208;&#178;&#208;&#184;&#209;&#130;&#209;&#140;'.link('/settings/undeleteAcc?user=' + result.login + '&key=' + result.key);
                else
                    er_msg.innerHTML = '&#208;&#155;&#208;&#190;&#208;&#179;&#208;&#184;&#208;&#189;/&#208;&#191;&#208;&#176;&#209;&#128;&#208;&#190;&#208;&#187;&#209;&#140; &#208;&#178;&#208;&#178;&#208;&#181;&#208;&#180;&#208;&#181;&#208;&#189;&#209;&#139; &#208;&#189;&#208;&#181;&#208;&#191;&#209;&#128;&#208;&#176;&#208;&#178;&#208;&#184;&#208;&#187;&#209;&#140;&#208;&#189;&#208;&#190;. &#208;&#159;&#208;&#190;&#208;&#191;&#209;&#128;&#208;&#190;&#208;&#177;&#209;&#131;&#208;&#185;&#209;&#130;&#208;&#181; &#208;&#181;&#209;&#137;&#208;&#181; &#209;&#128;&#208;&#176;&#208;&#183;.';

                _show(er_msg);

                disableForm(form, false);
                form.login.blur();
                trytofocus(form.login);

                if(callback)
                    callback(null, result.code);
            }
        );
        return false;
    }

/* &#208;&#147;&#208;&#181;&#208;&#189;&#208;&#181;&#209;&#128;&#208;&#184;&#209;&#128;&#208;&#190;&#208;&#178;&#208;&#176;&#208;&#189;&#208;&#184;&#208;&#181; &#208;&#191;&#208;&#190;&#208;&#180;&#208;&#191;&#208;&#184;&#209;&#129;&#208;&#181;&#208;&#185; &#208;&#186; &#209;&#135;&#208;&#184;&#209;&#129;&#208;&#187;&#208;&#184;&#209;&#130;&#208;&#181;&#208;&#187;&#209;&#140;&#208;&#189;&#209;&#139;&#208;&#188; */
function pluralForm(n, form1, form2, form5)
{
    n = Math.abs(n)%100;
    n1 = n%10;
    if(n > 10 && n < 20) return form5;
    if(n1 > 1 && n1 < 5) return form2;
    if(n1 == 1) return form1;
    return form5;
}

/* &#208;&#158;&#208;&#177;&#208;&#189;&#208;&#190;&#208;&#178;&#208;&#187;&#208;&#181;&#208;&#189;&#208;&#184;&#208;&#181; &#208;&#184;&#208;&#189;&#209;&#132;&#208;&#190;&#209;&#128;&#208;&#188;&#208;&#176;&#209;&#134;&#208;&#184;&#208;&#184; &#208;&#187;&#208;&#184;&#209;&#135;&#208;&#189;&#208;&#190;&#208;&#179;&#208;&#190; &#208;&#186;&#208;&#176;&#208;&#177;&#208;&#184;&#208;&#189;&#208;&#181;&#209;&#130;&#208;&#176; */
function updateOwnCabinet()
{
    if(!('reload_personal_url' in window))
        return;

    JsHttpRequest.query(
        window.reload_personal_url, null,
        function(result, debugMessages)
        {
            if(!(result instanceof Object) || debugMessages)
                return;

            setTimeout(updateOwnCabinet, 600000); //10 &#208;&#188;&#208;&#184;&#208;&#189;&#209;&#131;&#209;&#130;

            if(('fn' in result) && _$('qlm_greeting'))
                _$('qlm_greeting').innerHTML = getDayTime() + (result.fn.length ? (', ' + result.fn) : '');

            var item = false, t, titles = {
                mail: ['&#208;&#189;&#208;&#190;&#208;&#178;&#209;&#139;&#209;&#133; &#208;&#191;&#208;&#184;&#209;&#129;&#208;&#181;&#208;&#188; &#208;&#189;&#208;&#181;&#209;&#130;', '&#208;&#189;&#208;&#190;&#208;&#178;&#208;&#190;&#208;&#181; &#208;&#191;&#208;&#184;&#209;&#129;&#209;&#140;&#208;&#188;&#208;&#190;', '&#208;&#189;&#208;&#190;&#208;&#178;&#209;&#139;&#209;&#133; &#208;&#191;&#208;&#184;&#209;&#129;&#209;&#140;&#208;&#188;&#208;&#176;', '&#208;&#189;&#208;&#190;&#208;&#178;&#209;&#139;&#209;&#133; &#208;&#191;&#208;&#184;&#209;&#129;&#208;&#181;&#208;&#188;'],
                love: ['&#208;&#189;&#208;&#190;&#208;&#178;&#209;&#139;&#209;&#133; &#209;&#129;&#208;&#190;&#208;&#190;&#208;&#177;&#209;&#137;&#208;&#181;&#208;&#189;&#208;&#184;&#208;&#185; &#208;&#189;&#208;&#181;&#209;&#130;', '&#208;&#189;&#208;&#190;&#208;&#178;&#208;&#190;&#208;&#181; &#209;&#129;&#208;&#190;&#208;&#190;&#208;&#177;&#209;&#137;&#208;&#181;&#208;&#189;&#208;&#184;&#208;&#181;', '&#208;&#189;&#208;&#190;&#208;&#178;&#209;&#139;&#209;&#133; &#209;&#129;&#208;&#190;&#208;&#190;&#208;&#177;&#209;&#137;&#208;&#181;&#208;&#189;&#208;&#184;&#209;&#143;', '&#208;&#189;&#208;&#190;&#208;&#178;&#209;&#139;&#209;&#133; &#209;&#129;&#208;&#190;&#208;&#190;&#208;&#177;&#209;&#137;&#208;&#181;&#208;&#189;&#208;&#184;&#208;&#185;']
            };

            if(('mail' in result) && (item = _$('qhu_mail_top')))
            {
                t = titles['mail'];
                item.innerHTML = result['mail'] + ' ' + pluralForm(result['mail'], t[1], t[2], t[3]);
                _show(item.parentNode);
            }

            for(var name in titles)
            {
                if(!(name in result) || !(item = _$('qlmm_' + name)))
                    continue;

                t = titles[name];
                if(result[name] *= 1)
                {
                    setClass(item, 'q_bold');
                    item.innerHTML = result[name] + ' ' + pluralForm(result[name], t[1], t[2], t[3]);
                }
                else
                    item.innerHTML = t[0];
            }
        },
        true
    )
}

/* &#208;&#146;&#208;&#190;&#208;&#183;&#208;&#178;&#209;&#128;&#208;&#176;&#209;&#137;&#208;&#176;&#208;&#181;&#209;&#130; &#208;&#189;&#208;&#176;&#208;&#183;&#208;&#178;&#208;&#176;&#208;&#189;&#208;&#184;&#208;&#181; &#208;&#178;&#209;&#128;&#208;&#181;&#208;&#188;&#208;&#181;&#208;&#189;&#208;&#184; &#209;&#129;&#209;&#131;&#209;&#130;&#208;&#190;&#208;&#186; */
function getDayTime()
{
    var t = new Date().getHours();
    var d = new Date().getDay();
    var str_t='';
    if (t < 5) str_t = '&#208;&#148;&#208;&#190;&#208;&#177;&#209;&#128;&#208;&#190;&#208;&#185; &#208;&#189;&#208;&#190;&#209;&#135;&#208;&#184;';
    else if (t < 10) str_t = '&#208;&#148;&#208;&#190;&#208;&#177;&#209;&#128;&#208;&#190;&#208;&#181; &#209;&#131;&#209;&#130;&#209;&#128;&#208;&#190;';
    else if (t < 12 && (d == 0 || d == 6)) str_t = '&#208;&#148;&#208;&#190;&#208;&#177;&#209;&#128;&#208;&#190;&#208;&#181; &#209;&#131;&#209;&#130;&#209;&#128;&#208;&#190;';
    else if (t < 18) str_t = '&#208;&#148;&#208;&#190;&#208;&#177;&#209;&#128;&#209;&#139;&#208;&#185; &#208;&#180;&#208;&#181;&#208;&#189;&#209;&#140;';
    else str_t = '&#208;&#148;&#208;&#190;&#208;&#177;&#209;&#128;&#209;&#139;&#208;&#185; &#208;&#178;&#208;&#181;&#209;&#135;&#208;&#181;&#209;&#128;';
    return str_t;
}

function showLoginForm()
{
    var form = _$('qip_login_form');
    if(!_hidden(form))
        _hide(form);
    else
    {
        _show(form);
        form.login.select();
        trytofocus(form.login);
    }
    return false;
}

//&#208;&#191;&#208;&#181;&#209;&#128;&#208;&#181;&#209;&#133;&#208;&#190;&#208;&#180; &#208;&#189;&#208;&#176; &#208;&#191;&#208;&#190;&#208;&#184;&#209;&#129;&#208;&#186; &#208;&#191;&#209;&#128;&#208;&#184; &#208;&#189;&#208;&#176;&#208;&#187;&#208;&#184;&#209;&#135;&#208;&#184;&#208;&#184; &#208;&#178;&#208;&#178;&#208;&#181;&#208;&#180;&#208;&#181;&#208;&#189;&#208;&#189;&#208;&#190;&#208;&#179;&#208;&#190; &#208;&#183;&#208;&#176;&#208;&#191;&#209;&#128;&#208;&#190;&#209;&#129;&#208;&#176;
function qipGoSearch(link)
{
    var query = document.forms['qip_search_form'].query.value;
    if(query.length)
        link.href = link.className + query;
}

function qipInitSuggest()
{
    if(typeof(suggest) == 'undefined')
        return;
    suggest.init('qip_suggest', 'qip_search_form_input', 'qip_search_form', 'qip_search_form_submit', 'http://search.qip.ru/suggest?q=');
    suggest.goSearch = function(form) {
        suggest.hide();
        if((suggest.s.style.display == 'none' || suggest.sug_select == -1) && form.query.value.length)
            form.submit();
    }
}

function sample(span,url)
{
    if(url)
        JsHttpRequest.query(url,{},function(){},true);
    var field = (_$('search_form_text_internet') || _$('search_form_text') || _$('qip_search_form_input') || {});
    field.value = span.innerHTML;
    trytofocus(field);
}

function focusField(field, def_val)
{
    if(field.value != def_val)
        return;
    field.className = field.className.split(' ')[0];
    field.value = '';
}

function blurField(field, def_val)
{
    if(field.value != '')
        return;
    field.className = field.className + ' qh_field_inact';
    field.value = def_val;
}

function _$(id){return document.getElementById(id);}

/* &#209;&#129;&#208;&#190;&#208;&#183;&#208;&#180;&#208;&#176;&#208;&#189;&#208;&#184;&#208;&#181; &#209;&#141;&#208;&#187;&#208;&#181;&#208;&#188;&#208;&#181;&#208;&#189;&#209;&#130;&#208;&#176; &#209;&#129; &#208;&#176;&#209;&#130;&#209;&#128;&#208;&#184;&#208;&#177;&#209;&#131;&#209;&#130;&#208;&#176;&#208;&#188;&#208;&#184;, &#209;&#129;&#209;&#130;&#208;&#184;&#208;&#187;&#209;&#143;&#208;&#188;&#208;&#184; &#208;&#184; &#208;&#191;&#208;&#190;&#209;&#130;&#208;&#190;&#208;&#188;&#208;&#186;&#208;&#176;&#208;&#188;&#208;&#184; */
function _$$(tagName, attributes, style, childs)
{
    var element = document.createElement(tagName);
    if(attributes)
        for(var property in attributes)
            element[property] = attributes[property];
    if(childs)
        for(var i = 0, ln = childs.length; i < ln; i++)
            element.appendChild(childs[i]);
    return element;
}

function getStyle(element, property, format)
{
    var D = document,
        value = null;
    if(element.style[property])
        value = element.style[css2camel(property)];
    else if(D.defaultView && D.defaultView.getComputedStyle)
        value = D.defaultView.getComputedStyle(element, null).getPropertyValue(property);
    else if(element.currentStyle)
        value = element.currentStyle[css2camel(property)];

    if(format == 1)
        value = isNaN(value = parseInt(value)) ? 0 : value;
    else if(format == 2)
        value = isNaN(value = parseFloat(value)) ? 0 : value;

    return value;
}

function css2camel(property)
{
    if(property == 'float')
        return 'styleFloat';
    var pattern = /\-([a-z])/g;
    if(pattern.test(property))
        property = property.replace(pattern, function(){return arguments[1].toUpperCase();});
    return property;
}

function trytofocus(el){try{el.focus()}catch(e){};}

function setClass(elem, className){if(!hasClass(elem, className)){elem.className += ' ' + className;}}
function unsetClass(elem, className){elem.className = (' ' + elem.className + ' ').replace(' ' + className + ' ', ' ').slice(1, -1);}
function replaceClass(elem, oldClassName, newClassName){elem.className = (' ' + elem.className + ' ').replace(' ' + oldClassName + ' ', ' ' + newClassName + ' ').slice(1, -1);}
function hasClass(elem, className){return (elem.className == className) || ((' ' + elem.className + ' ').indexOf(' ' + className + ' ') != -1);}
function _show(elem){unsetClass(elem, 'q_hidden');}
function _hide(elem){setClass(elem, 'q_hidden');}
function _hidden(elem){return hasClass(elem, 'q_hidden');}


function closeMenu()
{
    setTimeout(hideLoginFrom, 200);
}
function hideLoginFrom(p)
{
    var form = _$('qip_login_form');
    if(form && (!form.login.disabled || p))
        _hide(form);
}

function show_more(hide)
{
    (!hide && hasClass(this, 'qm_inactive')) ? unsetClass(this, 'qm_inactive') : setClass(this, 'qm_inactive');
}

//&#209;&#129;&#208;&#190;&#209;&#133;&#209;&#128;&#208;&#176;&#208;&#189;&#208;&#181;&#208;&#189;&#208;&#184;&#208;&#181; &#208;&#189;&#208;&#176;&#209;&#129;&#209;&#130;&#209;&#128;&#208;&#190;&#208;&#181;&#208;&#186; &#209;&#129;&#209;&#130;&#209;&#128;&#208;&#176;&#208;&#189;&#208;&#184;&#209;&#134;&#209;&#139; &#208;&#180;&#208;&#187;&#209;&#143; qip.ru
function set_startqip_settings(fieldname, value, cookie_name, project)
{
    cookie_name = cookie_name || 'startqip_settings'; //&#208;&#184;&#208;&#188;&#209;&#143; &#208;&#186;&#209;&#131;&#208;&#186;&#208;&#184;

    var settings = getCookie(cookie_name);
    if(!settings) //&#208;&#186;&#209;&#131;&#208;&#186;&#208;&#176; &#208;&#189;&#208;&#181; &#209;&#129;&#209;&#131;&#209;&#137;&#208;&#181;&#209;&#129;&#209;&#130;&#208;&#178;&#209;&#131;&#208;&#181;&#209;&#130;
        settings = '';

    settings = _unpack(settings); //&#209;&#128;&#208;&#176;&#209;&#129;&#208;&#191;&#208;&#176;&#208;&#186;&#208;&#190;&#208;&#178;&#208;&#186;&#208;&#176;
    if(!(settings instanceof Object))
        settings = {};

    settings[fieldname] = value; //&#209;&#129;&#208;&#190;&#209;&#133;&#209;&#128;&#208;&#176;&#208;&#189;&#208;&#181;&#208;&#189;&#208;&#184;&#208;&#181; &#208;&#183;&#208;&#189;&#208;&#176;&#209;&#135;&#208;&#181;&#208;&#189;&#208;&#184;&#209;&#143;
    settings = _pack(settings); //&#209;&#131;&#208;&#191;&#208;&#176;&#208;&#186;&#208;&#190;&#208;&#178;&#208;&#186;&#208;&#176;

    project = project || '';

    setCookie(
        cookie_name,
        settings,
        new Date(new Date().getFullYear()+1, 1, 1),
        '/',
        (new RegExp(project+"(qip(2|3)?\.)?qip\.ru").test(document.domain) ? document.domain : (project+'.qip.ru'))
    );
}

function get_startqip_settings(field_name, cookie_name)
{
    cookie_name = cookie_name || 'startqip_settings'; //&#208;&#184;&#208;&#188;&#209;&#143; &#208;&#186;&#209;&#131;&#208;&#186;&#208;&#184;

    var settings = getCookie(cookie_name);
    if(!settings) //&#208;&#186;&#209;&#131;&#208;&#186;&#208;&#176; &#208;&#189;&#208;&#181; &#209;&#129;&#209;&#131;&#209;&#137;&#208;&#181;&#209;&#129;&#209;&#130;&#208;&#178;&#209;&#131;&#208;&#181;&#209;&#130;
        return null;

    settings = _unpack(settings); //&#209;&#128;&#208;&#176;&#209;&#129;&#208;&#191;&#208;&#176;&#208;&#186;&#208;&#190;&#208;&#178;&#208;&#186;&#208;&#176;
    if(!(settings instanceof Object)) //&#208;&#178; &#208;&#186;&#209;&#131;&#208;&#186;&#208;&#181; &#208;&#177;&#209;&#139;&#208;&#187;&#208;&#176; &#208;&#187;&#208;&#176;&#208;&#182;&#208;&#176;
        return null;

    return (field_name in settings) ? settings[field_name] : null;
}

//&#209;&#131;&#208;&#191;&#208;&#176;&#208;&#186;&#208;&#190;&#208;&#178;&#208;&#186;&#208;&#176; &#208;&#184; &#209;&#128;&#208;&#176;&#209;&#129;&#208;&#191;&#208;&#176;&#208;&#186;&#208;&#190;&#208;&#178;&#208;&#186;&#208;&#176; &#208;&#180;&#208;&#176;&#208;&#189;&#208;&#189;&#209;&#139;&#209;&#133; &#208;&#178; &#208;&#186;&#209;&#131;&#208;&#186;&#208;&#181;
function _pack(obj)
{
    var data = [];
    for(var field in obj)
        data.push(field+'='+obj[field]);
    return data.join('|');
}
function _unpack(packed)
{
    var data = packed.split('|'), obj = {};
    for(var i=0; i<data.length; i++)
    {
        data[i] = data[i].split('=');
        if(data[i].length === 2)
            obj[data[i][0]] = data[i][1];
    }
    return obj;
}

function disableForm(form, disable)
{
    var elems = form.elements;
    for(var i=0; i<elems.length; i++)
        elems[i].disabled = disable;
}

function checkAll(src_elem, target_elem_name)
{
    var elems = src_elem.form.elements;
    for(var i=0; i<elems.length; i++)
        if(elems[i].type.toLowerCase() == 'checkbox' && (elems[i].name == target_elem_name || elems[i].name == src_elem.name))
            elems[i].checked = src_elem.checked;
}

function setCookie(name, value, expires, path, domain, secure)
{
    var curCookie = name + "=" + escape(value) +
        ((expires) ? "; expires=" + expires.toGMTString() : "") +
        ((path) ? "; path=" + path : "") +
        ((domain) ? "; domain=" + domain : "") +
        ((secure) ? "; secure" : "");
    document.cookie = curCookie;
}

function getCookie(name)
{
    var prefix = name + "=";
    var cookieStartIndex = document.cookie.indexOf(prefix);
    if (cookieStartIndex == -1)
        return null;
    var cookieEndIndex = document.cookie.indexOf(";", cookieStartIndex + prefix.length);
    if (cookieEndIndex == -1)
        cookieEndIndex = document.cookie.length;
    return unescape(document.cookie.substring(cookieStartIndex + prefix.length, cookieEndIndex));
}

function deleteCookie(name, path, domain)
{
    if (getCookie(name))
    {
        document.cookie = name + "=" +
            ((path) ? "; path=" + path : "") +
            ((domain) ? "; domain=" + domain : "") +
            "; expires=Thu, 01-Jan-70 00:00:01 GMT";
    }
}

/* &#208;&#180;&#208;&#187;&#209;&#143; &#209;&#141;&#208;&#187;&#208;&#181;&#208;&#188;&#208;&#181;&#208;&#189;&#209;&#130;&#208;&#176; elem &#208;&#178;&#208;&#190;&#208;&#183;&#208;&#178;&#209;&#128;&#208;&#176;&#209;&#137;&#208;&#176;&#208;&#181;&#209;&#130; &#209;&#128;&#208;&#190;&#208;&#180;&#208;&#184;&#209;&#130;&#208;&#181;&#208;&#187;&#209;&#143; (&#208;&#187;&#209;&#142;&#208;&#177;&#208;&#190;&#208;&#185; &#208;&#178;&#208;&#187;&#208;&#190;&#208;&#182;&#208;&#181;&#208;&#189;&#208;&#189;&#208;&#190;&#209;&#129;&#209;&#130;&#208;&#184;) &#209;&#129; &#209;&#130;&#208;&#181;&#208;&#179;&#208;&#190;&#208;&#188; parent_tag_name, &#208;&#181;&#209;&#129;&#208;&#187;&#208;&#184; &#208;&#189;&#208;&#176;&#208;&#185;&#208;&#180;&#208;&#181;&#208;&#189;, &#208;&#184;&#208;&#189;&#208;&#176;&#209;&#135;&#208;&#181; - false */
function getParentByTagName(elem, parent_tag_name)
{
    var cur_tag_name = elem.tagName.toLowerCase(), parent_tag_name = parent_tag_name.toLowerCase();
    while(cur_tag_name !== parent_tag_name && cur_tag_name !== 'html')
        elem = elem.parentNode, cur_tag_name = elem.tagName.toLowerCase();
    return (cur_tag_name === 'html') ? false : elem;
}

/* &#208;&#191;&#209;&#128;&#208;&#190;&#208;&#178;&#208;&#181;&#209;&#128;&#209;&#143;&#208;&#181;&#209;&#130; &#208;&#178;&#208;&#181;&#209;&#128;&#209;&#129;&#208;&#184;&#209;&#142; &#208;&#177;&#209;&#128;&#208;&#176;&#209;&#131;&#208;&#183;&#208;&#181;&#209;&#128;&#208;&#176; &#208;&#184; &#208;&#191;&#208;&#190;&#208;&#186;&#208;&#176;&#208;&#183;&#209;&#139;&#208;&#178;&#208;&#176;&#208;&#181;&#209;&#130; &#208;&#178;&#209;&#129;&#208;&#191;&#208;&#187;&#209;&#139;&#208;&#178;&#208;&#176;&#209;&#136;&#208;&#186;&#209;&#131; &#209;&#129; &#208;&#191;&#209;&#128;&#208;&#181;&#208;&#180;&#208;&#187;&#208;&#190;&#208;&#182;&#208;&#181;&#208;&#189;&#208;&#184;&#208;&#181;&#208;&#188; &#208;&#190;&#208;&#177;&#208;&#189;&#208;&#190;&#208;&#178;&#208;&#184;&#209;&#130;&#209;&#140;&#209;&#129;&#209;&#143;, &#208;&#181;&#209;&#129;&#208;&#187;&#208;&#184; &#208;&#190;&#208;&#189; &#209;&#131;&#209;&#129;&#209;&#130;&#208;&#176;&#209;&#128;&#208;&#181;&#208;&#187; */
function qipBrowserReject()
{
    var ua = navigator.userAgent;
    if(    (!ua.match(/(opera\b)(?:.+version\/|[/ ])(\d+\.\d+)/i) && !ua.match(/ms(ie) (\d+\.\d+)/i) && !ua.match(/(firefox)\/(\d+\.\d+)/i))
        || (RegExp.$2*1 >= {ie: 8, firefox: 3, opera: 11}[RegExp.$1.toLowerCase()])
        || (getCookie('qip_browser_reject') != null)
        ) return;

    setCookie('qip_browser_reject', 1, new Date(+new Date + 86400000), '/', '.qip.ru');

    document.domain = 'qip.ru';

    setClass(document.body.parentNode, 'q_reject_root');

    document.getElementsByTagName('head')[0].appendChild(
        <fetcher.fetch.extensions.js_aux.browser.HtmlWindow object at 0xb5ead30c>
        _$$('link', {id: 'q_reject_stylesheet_link', rel: 'stylesheet', href: '/reject/reject.css'})
        );
        document.body.insertBefore(_$$('div', {
            id: 'q_reject_darkbox', className: 'q_reject_darkbox', title: ua,
            innerHTML: '<div class="qr_container"><iframe class="qrc_iframe" src="/reject/reject.html" frameborder="0" scrolling="no"></iframe></div>'
            }), document.body.firstChild);
        }

        function qipBrowserRejectClose()
{
    var link = _$('q_reject_stylesheet_link'), reject = _$('q_reject_darkbox');
    link && link.parentNode.removeChild(link), reject && reject.parentNode.removeChild(reject);
    unsetClass(document.body.parentNode, 'q_reject_root');
    }

        DEBUG:html.window:executing script: /**
        * JsHttpRequest: JavaScript "AJAX" data loader
        * @license LGPL
        * @author Dmitry Koterov, http://en.dklab.ru/lib/JsHttpRequest/
        */
        function JsHttpRequest(){
            var t=this;
            t.onreadystatechange=null;
            t.readyState=0;
            t.responseText=null;
            t.responseXML=null;
            t.status=200;
            t.statusText="OK";
            t.responseJS=null;
            t.caching=false;
            t.loader=null;
            t.session_name="PHPSESSID";
            t._ldObj=null;
            t._reqHeaders=[];
            t._openArgs=null;
            t._errors={inv_form_el:"Invalid FORM element detected: name=%, tag=%",must_be_single_el:"If used, <form> must be a single HTML element in the list.",js_invalid:"JavaScript code generated by backend is invalid!\n%",url_too_long:"Cannot use so long query with GET request (URL is larger than % bytes)",unk_loader:"Unknown loader: %",no_loaders:"No loaders registered at all, please check JsHttpRequest.LOADERS array",no_loader_matched:"Cannot find a loader which may process the request. Notices are:\n%"};
        t.abort=function(){
            with(this){
            if(_ldObj&&_ldObj.abort){
            _ldObj.abort();
            }
        _cleanup();
        if(readyState==0){
            return;
            }
        if(readyState==1&&!_ldObj){
            readyState=0;
            return;
            }
        _changeReadyState(4,true);
        }
        };
        t.open=function(_2,_3,_4,_5,_6){
            with(this){
            if(_3.match(/^((\w+)\.)?(GET|POST)\s+(.*)/i)){
            this.loader=RegExp.$2?RegExp.$2:null;
            _2=RegExp.$3;
            _3=RegExp.$4;
            }
        try{
            if(document.location.search.match(new RegExp("[&?]"+session_name+"=([^&?]*)"))||document.cookie.match(new RegExp("(?:;|^)\\s*"+session_name+"=([^;]*)"))){
            _3+=(_3.indexOf("?")>=0?"&":"?")+session_name+"="+this.escape(RegExp.$1);
            }
        }
        catch(e){
            }
        _openArgs={method:(_2||"").toUpperCase(),url:_3,asyncFlag:_4,username:_5!=null?_5:"",password:_6!=null?_6:""};
        _ldObj=null;
        _changeReadyState(1,true);
        return true;
        }
        };
        t.send=function(_7){
            if(!this.readyState){
            return;
            }
        this._changeReadyState(1,true);
        this._ldObj=null;
        var _8=[];
        var _9=[];
        if(!this._hash2query(_7,null,_8,_9)){
            return;
            }
        var _a=null;
        if(this.caching&&!_9.length){
            _a=this._openArgs.username+":"+this._openArgs.password+"@"+this._openArgs.url+"|"+_8+"#"+this._openArgs.method;
            var _b=JsHttpRequest.CACHE[_a];
            if(_b){
            this._dataReady(_b[0],_b[1]);
            return false;
            }
        }
        var _c=(this.loader||"").toLowerCase();
        if(_c&&!JsHttpRequest.LOADERS[_c]){
            return this._error("unk_loader",_c);
            }
        var _d=[];
        var _e=JsHttpRequest.LOADERS;
        for(var _f in _e){
            var ldr=_e[_f].loader;
            if(!ldr){
            continue;
            }
        if(_c&&_f!=_c){
            continue;
            }
        var _11=new ldr(this);
        JsHttpRequest.extend(_11,this._openArgs);
        JsHttpRequest.extend(_11,{queryText:_8.join("&"),queryElem:_9,id:(new Date().getTime())+""+JsHttpRequest.COUNT++,hash:_a,span:null});
        var _12=_11.load();
        if(!_12){
            this._ldObj=_11;
            JsHttpRequest.PENDING[_11.id]=this;
            return true;
            }
        if(!_c){
            _d[_d.length]="- "+_f.toUpperCase()+": "+this._l(_12);
            }else{
            return this._error(_12);
            }
        }
        return _f?this._error("no_loader_matched",_d.join("\n")):this._error("no_loaders");
        };
        t.getAllResponseHeaders=function(){
            with(this){
            return _ldObj&&_ldObj.getAllResponseHeaders?_ldObj.getAllResponseHeaders():[];
            }
        };
        t.getResponseHeader=function(_13){
            with(this){
            return _ldObj&&_ldObj.getResponseHeader?_ldObj.getResponseHeader(_13):null;
            }
        };
        t.setRequestHeader=function(_14,_15){
            with(this){
            _reqHeaders[_reqHeaders.length]=[_14,_15];
            }
        };
        t._dataReady=function(_16,js){
            with(this){
            if(caching&&_ldObj){
            JsHttpRequest.CACHE[_ldObj.hash]=[_16,js];
            }
        responseText=responseXML=_16;
        responseJS=js;
        if(js!==null){
            status=200;
            statusText="OK";
            }else{
            status=500;
            statusText="Internal Server Error";
            }
        _changeReadyState(2);
        _changeReadyState(3);
        _changeReadyState(4);
        _cleanup();
        }
        };
        t._l=function(_18){
            var i=0,p=0,msg=this._errors[_18[0]];
            while((p=msg.indexOf("%",p))>=0){
            var a=_18[++i]+"";
            msg=msg.substring(0,p)+a+msg.substring(p+1,msg.length);
            p+=1+a.length;
            }
        return msg;
        };
        t._error=function(msg){
            msg=this._l(typeof (msg)=="string"?arguments:msg);
            msg="JsHttpRequest: "+msg;
            if(!window.Error){
            throw msg;
            }else{
            if((new Error(1,"test")).description=="test"){
            throw new Error(1,msg);
            }else{
            throw new Error(msg);
            }
        }
        };
        t._hash2query=function(_1e,_1f,_20,_21){
            if(_1f==null){
            _1f="";
            }
        if((""+typeof (_1e)).toLowerCase()=="object"){
            var _22=false;
            if(_1e&&_1e.parentNode&&_1e.parentNode.appendChild&&_1e.tagName&&_1e.tagName.toUpperCase()=="FORM"){
            _1e={form:_1e};
        }
        for(var k in _1e){
            var v=_1e[k];
            if(v instanceof Function){
            continue;
            }
        var _25=_1f?_1f+"["+this.escape(k)+"]":this.escape(k);
        var _26=v&&v.parentNode&&v.parentNode.appendChild&&v.tagName;
        if(_26){
            var tn=v.tagName.toUpperCase();
            if(tn=="FORM"){
            _22=true;
            }else{
            if(tn=="INPUT"||tn=="TEXTAREA"||tn=="SELECT"){
            }else{
            return this._error("inv_form_el",(v.name||""),v.tagName);
            }
        }
        _21[_21.length]={name:_25,e:v};
        }else{
            if(v instanceof Object){
            this._hash2query(v,_25,_20,_21);
            }else{
            if(v===null){
            continue;
            }
        if(v===true){
            v=1;
            }
        if(v===false){
            v="";
            }
        _20[_20.length]=_25+"="+this.escape(""+v);
        }
        }
        if(_22&&_21.length>1){
            return this._error("must_be_single_el");
            }
        }
        }else{
            _20[_20.length]=_1e;
            }
        return true;
        };
        t._cleanup=function(){
            var _28=this._ldObj;
            if(!_28){
            return;
            }
        JsHttpRequest.PENDING[_28.id]=false;
        var _29=_28.span;
        if(!_29){
            return;
            }
        _28.span=null;
        var _2a=function(){
            _29.parentNode.removeChild(_29);
            };
        JsHttpRequest.setTimeout(_2a,50);
        };
        t._changeReadyState=function(s,_2c){
            with(this){
            if(_2c){
            status=statusText=responseJS=null;
            responseText="";
            }
        readyState=s;
        if(onreadystatechange){
            onreadystatechange();
            }
        }
        };
        t.escape=function(s){
            return escape(s).replace(new RegExp("\\+","g"),"%2B");
            };
        }
        JsHttpRequest.COUNT=0;
        JsHttpRequest.MAX_URL_LEN=2000;
        JsHttpRequest.CACHE={};
        JsHttpRequest.PENDING={};
        JsHttpRequest.LOADERS={};
        JsHttpRequest._dummy=function(){
            };
        JsHttpRequest.TIMEOUTS={s:window.setTimeout,c:window.clearTimeout};
        JsHttpRequest.setTimeout=function(_2e,dt){
            window.JsHttpRequest_tmp=JsHttpRequest.TIMEOUTS.s;
            if(typeof (_2e)=="string"){
            id=window.JsHttpRequest_tmp(_2e,dt);
            }else{
            var id=null;
            var _31=function(){
            _2e();
            delete JsHttpRequest.TIMEOUTS[id];
            };
        id=window.JsHttpRequest_tmp(_31,dt);
        JsHttpRequest.TIMEOUTS[id]=_31;
        }
        window.JsHttpRequest_tmp=null;
        return id;
        };
        JsHttpRequest.clearTimeout=function(id){
            window.JsHttpRequest_tmp=JsHttpRequest.TIMEOUTS.c;
            delete JsHttpRequest.TIMEOUTS[id];
            var r=window.JsHttpRequest_tmp(id);
            window.JsHttpRequest_tmp=null;
            return r;
            };
        JsHttpRequest.query=function(url,_35,_36,_37){
            var req=new this();
            req.caching=!_37;
            req.onreadystatechange=function(){
            if(req.readyState==4){
            _36(req.responseJS,req.responseText);
            }
        };
        req.open(null,url,true);
        req.send(_35);
        };
        JsHttpRequest.dataReady=function(d){
            var th=this.PENDING[d.id];
            delete this.PENDING[d.id];
            if(th){
            th._dataReady(d.text,d.js);
            }else{
            if(th!==false){
            throw "dataReady(): unknown pending id: "+d.id;
            }
        }
        };
        JsHttpRequest.extend=function(_3b,src){
            for(var k in src){
            _3b[k]=src[k];
            }
        };
        JsHttpRequest.LOADERS.xml={loader:function(req){
            JsHttpRequest.extend(req._errors,{xml_no:"Cannot use XMLHttpRequest or ActiveX loader: not supported",xml_no_diffdom:"Cannot use XMLHttpRequest to load data from different domain %",xml_no_headers:"Cannot use XMLHttpRequest loader or ActiveX loader, POST method: headers setting is not supported, needed to work with encodings correctly",xml_no_form_upl:"Cannot use XMLHttpRequest loader: direct form elements using and uploading are not implemented"});
        this.load=function(){
            if(this.queryElem.length){
            return ["xml_no_form_upl"];
            }
        if(this.url.match(new RegExp("^([a-z]+://[^\\/]+)(.*)","i"))){
            if(RegExp.$1.toLowerCase()!=document.location.protocol+"//"+document.location.hostname.toLowerCase()){
            return ["xml_no_diffdom",RegExp.$1];
            }
        }
        var xr=null;
        if(window.XMLHttpRequest){
            try{
            xr=new XMLHttpRequest();
            }
        catch(e){
            }
        }else{
            if(window.ActiveXObject){
            try{
            xr=new ActiveXObject("Microsoft.XMLHTTP");
            }
        catch(e){
            }
        if(!xr){
            try{
            xr=new ActiveXObject("Msxml2.XMLHTTP");
            }
        catch(e){
            }
        }
        }
        }
        if(!xr){
            return ["xml_no"];
            }
        var _40=window.ActiveXObject||xr.setRequestHeader;
        if(!this.method){
            this.method=_40&&this.queryText.length?"POST":"GET";
            }
        if(this.method=="GET"){
            if(this.queryText){
            this.url+=(this.url.indexOf("?")>=0?"&":"?")+this.queryText;
            }
        this.queryText="";
        if(this.url.length>JsHttpRequest.MAX_URL_LEN){
            return ["url_too_long",JsHttpRequest.MAX_URL_LEN];
            }
        }else{
            if(this.method=="POST"&&!_40){
            return ["xml_no_headers"];
            }
        }
        this.url+=(this.url.indexOf("?")>=0?"&":"?")+"JsHttpRequest="+(req.caching?"0":this.id)+"-xml";
        var id=this.id;
        xr.onreadystatechange=function(){
            if(xr.readyState!=4){
            return;
            }
        xr.onreadystatechange=JsHttpRequest._dummy;
        req.status=null;
        try{
            req.status=xr.status;
            req.responseText=xr.responseText;
            }
        catch(e){
            }
        if(!req.status){
            return;
            }
        try{
            if(req.responseText.indexOf("<html>")==0)
            return;
            var _42=req.responseText||"{ js: null, text: null }";
        eval("JsHttpRequest._tmp = function(id) { var d = "+_42+"; d.id = id; JsHttpRequest.dataReady(d); }");
        }
        catch(e){
            return req._error("js_invalid",req.responseText);
            }
        JsHttpRequest._tmp(id);
        JsHttpRequest._tmp=null;
        };
        xr.open(this.method,this.url,true,this.username,this.password);
        if(_40){
            for(var i=0;i<req._reqHeaders.length;i++){
            xr.setRequestHeader(req._reqHeaders[i][0],req._reqHeaders[i][1]);
            }
        xr.setRequestHeader("Content-Type","application/octet-stream");
        }
        xr.send(this.queryText);
        this.span=null;
        this.xr=xr;
        return null;
        };
        this.getAllResponseHeaders=function(){
            return this.xr.getAllResponseHeaders();
            };
        this.getResponseHeader=function(_44){
            return this.xr.getResponseHeader(_44);
            };
        this.abort=function(){
            this.xr.abort();
            this.xr=null;
            };
        }};
        JsHttpRequest.LOADERS.script={loader:function(req){
            JsHttpRequest.extend(req._errors,{script_only_get:"Cannot use SCRIPT loader: it supports only GET method",script_no_form:"Cannot use SCRIPT loader: direct form elements using and uploading are not implemented"});
        this.load=function(){
            if(this.queryText){
            this.url+=(this.url.indexOf("?")>=0?"&":"?")+this.queryText;
            }
        this.url+=(this.url.indexOf("?")>=0?"&":"?")+"JsHttpRequest="+this.id+"-"+"script";
        this.queryText="";
        if(!this.method){
            this.method="GET";
            }
        if(this.method!=="GET"){
            return ["script_only_get"];
            }
        if(this.queryElem.length){
            return ["script_no_form"];
            }
        if(this.url.length>JsHttpRequest.MAX_URL_LEN){
            return ["url_too_long",JsHttpRequest.MAX_URL_LEN];
            }
        var th=this,d=document,s=null,b=d.body;
        if(!window.opera){
            this.span=s=d.createElement("SCRIPT");
            var _4a=function(){
            s.language="JavaScript";
            if(s.setAttribute){
            s.setAttribute("src",th.url);
            }else{
            s.src=th.url;
            }
        b.insertBefore(s,b.lastChild);
        };
        }else{
            this.span=s=d.createElement("SPAN");
            s.style.display="none";
            b.insertBefore(s,b.lastChild);
            s.innerHTML="Workaround for IE.<s"+"cript></"+"script>";
            var _4a=function(){
            s=s.getElementsByTagName("SCRIPT")[0];
            s.language="JavaScript";
            if(s.setAttribute){
            s.setAttribute("src",th.url);
            }else{
            s.src=th.url;
            }
        };
        }
        JsHttpRequest.setTimeout(_4a,10);
        return null;
        };
        }};
        JsHttpRequest.LOADERS.form={loader:function(req){
            JsHttpRequest.extend(req._errors,{form_el_not_belong:"Element \"%\" does not belong to any form!",form_el_belong_diff:"Element \"%\" belongs to a different form. All elements must belong to the same form!",form_el_inv_enctype:"Attribute \"enctype\" of the form must be \"%\" (for IE), \"%\" given."});
        this.load=function(){
            var th=this;
            if(!th.method){
            th.method="POST";
            }
        th.url+=(th.url.indexOf("?")>=0?"&":"?")+"JsHttpRequest="+th.id+"-"+"form";
        if(th.method=="GET"){
            if(th.queryText){
            th.url+=(th.url.indexOf("?")>=0?"&":"?")+th.queryText;
            }
        if(th.url.length>JsHttpRequest.MAX_URL_LEN){
            return ["url_too_long",JsHttpRequest.MAX_URL_LEN];
            }
        var p=th.url.split("?",2);
        th.url=p[0];
        th.queryText=p[1]||"";
        }
        var _4e=null;
        var _4f=false;
        if(th.queryElem.length){
            if(th.queryElem[0].e.tagName.toUpperCase()=="FORM"){
            _4e=th.queryElem[0].e;
            _4f=true;
            th.queryElem=[];
            }else{
            _4e=th.queryElem[0].e.form;
            for(var i=0;i<th.queryelem.length><form></form>")+"<iframe name=""></iframe>";
            if(!_4e){
            _4e=th.span.firstChild;
            }
        d.body.insertBefore(s,d.body.lastChild);
        var _57=function(e,_59){
            var sv=[];
            var _5b=e;
            if(e.mergeAttributes){
            var _5b=d.createElement("form");
            _5b.mergeAttributes(e,false);
            }
        for(var i=0;i<_59.length;i++){
            var k=_59[i][0],v=_59[i][1];
            sv[sv.length]=[k,_5b.getAttribute(k)];
            _5b.setAttribute(k,v);
            }
        if(e.mergeAttributes){
            e.mergeAttributes(_5b,false);
            }
        return sv;
        };
        var _5f=function(){
            top.JsHttpRequestGlobal=JsHttpRequest;
            var _60=[];
            if(!_4f){
            for(var i=0,n=_4e.elements.length;i<n>=0;i--){
            var _64=qt[i].split("=",2);
            var e=d.createElement("INPUT");
            e.type="hidden";
            e.name=unescape(_64[0]);
            e.value=_64[1]!=null?unescape(_64[1]):"";
            _4e.appendChild(e);
            }
        for(var i=0;i<th.queryelem.length><qt.length><n>
            Traceback (most recent call last):
            File "/home/alex/projects/fetcher/samples/qip.py", line 26, in <module>
                qip_ru.start()
                File "/home/alex/projects/fetcher/fetcher/multifetch/__init__.py", line 49, in start
                self._process_finished_task(finished_task, error)
                File "/home/alex/projects/fetcher/fetcher/multifetch/__init__.py", line 154, in _process_finished_task
                self._process_for_tasks(handler(*args))
                File "/home/alex/projects/fetcher/fetcher/multifetch/__init__.py", line 105, in task__script_loaded
                self._process_finished_task(old_task)
                File "/home/alex/projects/fetcher/fetcher/multifetch/__init__.py", line 154, in _process_finished_task
                self._process_for_tasks(handler(*args))
                File "/home/alex/projects/fetcher/samples/qip.py", line 19, in task_main
                task.js.fireOnloadEvents()
                File "/home/alex/projects/fetcher/fetcher/fetch/extensions/js_aux/browser.py", line 502, in fireOnloadEvents
                self.evalScript(tag.string, tag=tag)
                File "/home/alex/projects/fetcher/fetcher/fetch/extensions/js_aux/browser.py", line 498, in evalScript
                ctxt.eval(script)
                SyntaxError: SyntaxError: Unexpected identifier (  @ 493 : 35 )  -> for(var i=0;i<th.queryelem.length><form></form>")+"<iframe name=""></iframe>";

                    Process finished with exit code 1
