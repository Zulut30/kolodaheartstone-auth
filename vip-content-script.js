jQuery(document).ready(function($) {
    console.log('VIP Script Loaded Successfully');

    // Функция декодирования (Base64 + ROT13 + UTF-8 Fix)
    function vipDecodeContent(encoded) {
        try {
            var base64Decoded = atob(encoded);
            var rot13Decoded = base64Decoded.replace(/[a-zA-Z]/g, function(c) {
                var charCode = c.charCodeAt(0);
                var offset = (charCode <= 90) ? 65 : 97;
                return String.fromCharCode(((charCode - offset + 13) % 26) + offset);
            });
            return decodeURIComponent(escape(rot13Decoded));
        } catch (e) {
            console.error('Content decoding failed:', e);
            return '';
        }
    }

    // Реинициализация сторонних плагинов (Simple Lightbox, спойлеры, шорткоды и пр.)
    // на контенте, который был динамически вставлен после ввода кода доступа.
    function vipReinitThirdPartyPlugins($content) {
        try {
            // 1) Стандартные события WordPress / сторонних плагинов
            $(document).trigger('post-load');
            $(document.body).trigger('post-load');
            $(document).trigger('content_updated', [$content]);
            $(document).trigger('vip-content-unlocked', [$content]);

            // 2) Simple Lightbox (by Archetyped) — пересканирование ссылок.
            //    У плагина есть глобал SLB. Пробуем все известные публичные методы.
            if (window.SLB) {
                try {
                    var slb = window.SLB;
                    if (slb.View && typeof slb.View.activate === 'function') {
                        slb.View.activate($content.get(0));
                    }
                    if (typeof slb.activate === 'function') {
                        slb.activate($content.get(0));
                    }
                    if (slb.Content_Handlers && typeof slb.Content_Handlers.init === 'function') {
                        slb.Content_Handlers.init();
                    }
                    if (slb.Viewer && typeof slb.Viewer.init === 'function') {
                        slb.Viewer.init();
                    }
                    // Принудительно триггерим ready-событие jQuery, на которое SLB вешает init
                    $(document).trigger('ready');
                } catch (e) { console.warn('VIP: SLB reinit failed', e); }
            }

            // 2b) Fallback для Simple Lightbox / lightbox2 / любых lightbox-плагинов:
            // добавляем класс, который SLB использует для авто-биндинга, и триггерим клик-делегацию.
            // Многие плагины ищут <a> с href на изображение. Клонируем и возвращаем, чтобы
            // документ-ready биндинги перехватили новые элементы.
            $content.find('a').each(function() {
                var $a = $(this);
                var href = ($a.attr('href') || '').toLowerCase();
                if (/\.(jpe?g|png|gif|webp|bmp|svg|avif)(\?.*)?$/i.test(href)) {
                    // Добавляем метки, которые распознают популярные lightbox-плагины
                    if (!$a.attr('data-lightbox')) $a.attr('data-lightbox', 'vip-gallery');
                    if (!$a.attr('rel')) $a.attr('rel', 'lightbox');
                    $a.addClass('slb-active');
                }
            });

            // 3) Другие популярные lightbox-плагины (FancyBox, Lity, Magnific, Lightbox2)
            if (window.jQuery && window.jQuery.fn) {
                try {
                    if (typeof window.jQuery.fn.fancybox === 'function') {
                        $content.find('[data-fancybox], a.fancybox').fancybox();
                    }
                    if (typeof window.jQuery.fn.magnificPopup === 'function') {
                        $content.find('.mfp, [data-mfp-src], a.popup-gallery').each(function(){
                            $(this).magnificPopup({type:'image'});
                        });
                    }
                } catch (e) { console.warn('VIP: lightbox reinit failed', e); }
            }
            if (typeof window.lightbox !== 'undefined' && window.lightbox && typeof window.lightbox.init === 'function') {
                try { window.lightbox.init(); } catch (e) {}
            }

            // 4) Принудительно запускаем скрипты <script> внутри вставленного контента
            //    (jQuery.html() не исполняет inline-скрипты в некоторых версиях)
            $content.find('script').each(function () {
                var src = this.src;
                var s = document.createElement('script');
                if (src) {
                    s.src = src;
                } else {
                    s.text = this.textContent || this.innerText || '';
                }
                if (this.type) s.type = this.type;
                document.head.appendChild(s).parentNode.removeChild(s);
            });

            // 5) Заново обрабатываем встраиваемые iframe/медиа
            if (window.wp && window.wp.mediaelement) {
                $(document).trigger('wp-mediaelement-initialize');
            }
            $(window).trigger('resize');
        } catch (err) {
            console.warn('VIP: third-party reinit error', err);
        }
    }

    // Функция разблокировки
    function vipUnlockContent(wrapper) {
        var idHash = wrapper.data('vip-hash');
        var scriptTemplate = wrapper.find('script[type="text/template"][data-vip-id="' + idHash + '"]');

        if (scriptTemplate.length > 0) {
            var encodedContent = scriptTemplate.text().trim();
            if (!encodedContent) return false;

            var decodedContent = vipDecodeContent(encodedContent);

            if (decodedContent) {
                wrapper.addClass('vip-is-unlocked'); // Расширяем контейнер

                var lockOverlay = wrapper.find('.vip-lock-overlay');
                var contentDiv = $('<div class="vip-unlocked-content" style="display:none"></div>').html(decodedContent);

                lockOverlay.after(contentDiv);
                lockOverlay.fadeOut(300, function() {
                    $(this).remove();
                    contentDiv.fadeIn(400, function() {
                        vipReinitThirdPartyPlugins(contentDiv);
                    });
                    $(window).trigger('resize');
                });
                return true;
            }
        }
        return false;
    }

    // Dropdown подписки (Telegram / Boosty / Tribute)
    $(document).on('click', '.vip-subscribe-toggle', function(e) {
        e.preventDefault();
        e.stopPropagation();
        var $dd = $(this).closest('.vip-subscribe-dropdown');
        var isOpen = $dd.hasClass('is-open');
        $('.vip-subscribe-dropdown.is-open').removeClass('is-open')
            .find('.vip-subscribe-toggle').attr('aria-expanded', 'false');
        if (!isOpen) {
            $dd.addClass('is-open');
            $(this).attr('aria-expanded', 'true');
        }
    });
    $(document).on('click', function() {
        $('.vip-subscribe-dropdown.is-open').removeClass('is-open')
            .find('.vip-subscribe-toggle').attr('aria-expanded', 'false');
    });
    $(document).on('keydown', function(e) {
        if (e.key === 'Escape') {
            $('.vip-subscribe-dropdown.is-open').removeClass('is-open')
                .find('.vip-subscribe-toggle').attr('aria-expanded', 'false');
        }
    });

    // Инициализация при загрузке
    function vipInitUnlock() {
        $('.vip-wrapper').each(function() {
            var wrapper = $(this);
            var idHash = wrapper.data('vip-hash');
            if (!idHash) return;
            
            var cookieName = 'vip_' + idHash;
            if (document.cookie.indexOf(cookieName + '=ok') !== -1) {
                vipUnlockContent(wrapper);
            }
        });
    }

    // КЛИК ПО КНОПКЕ
    $(document).on('click', '.vip-btn', function(e) {
        e.preventDefault();
        var btn = $(this);
        var wrapper = btn.closest('.vip-wrapper');
        var codeInput = wrapper.find('.vip-code');
        var code = codeInput.val().trim();
        var id = wrapper.data('id');
        var msg = wrapper.find('.vip-msg');
        
        if (!btn.data('default-text')) btn.data('default-text', btn.text());

        msg.removeClass('success error').text('');
        
        if (!code) {
            msg.addClass('error').text('Введите код');
            codeInput.focus();
            return;
        }

        var captchaData = '';
        if (wrapper.find('.vip-captcha').is(':visible') && typeof grecaptcha !== 'undefined') {
            captchaData = grecaptcha.getResponse();
            if (!captchaData) {
                msg.addClass('error').text('Подтвердите капчу');
                return;
            }
        }

        btn.prop('disabled', true).text('Проверка...');

        if (typeof vipData === 'undefined') {
             console.error('VIP Error: vipData is missing');
             alert('Ошибка: настройки не загружены. Обновите страницу.');
             btn.prop('disabled', false).text(btn.data('default-text'));
             return;
        }

        $.post(vipData.ajax, {
            action: 'vip_verify',
            code: code,
            id: id,
            recaptcha: captchaData,
            nonce: vipData.nonce
        }, function(res) {
            if (res.success) {
                msg.addClass('success').text(res.data.msg);
                setTimeout(function() {
                    var unlocked = vipUnlockContent(wrapper);
                    if (!unlocked) {
                        location.reload(); 
                    }
                }, 500);
            } else {
                btn.prop('disabled', false).text(btn.data('default-text'));
                msg.addClass('error').text(res.data.msg);
                
                if (res.data.show_captcha) {
                    var captchaBlock = wrapper.find('.vip-captcha');
                    if (captchaBlock.length > 0) {
                        captchaBlock.slideDown();
                        if (typeof grecaptcha !== 'undefined') grecaptcha.reset();
                    } else {
                        location.reload();
                    }
                }
            }
        }).fail(function() {
            msg.addClass('error').text('Ошибка сервера');
            btn.prop('disabled', false).text(btn.data('default-text'));
        });
    });
    
    vipInitUnlock();
    
    $(document).on('keypress', '.vip-code', function(e) {
        if (e.which === 13) $(this).closest('.vip-wrapper').find('.vip-btn').click();
    });
}); 
// Здесь больше НЕТ лишней скобки