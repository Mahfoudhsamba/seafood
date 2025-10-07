(function ($) {
  $(document).ready(function () {

     // sticky header active
     if ($("#header").length > 0) {
      $(window).on("scroll", function (event) {
        var scroll = $(window).scrollTop();
        if (scroll < 1) {
          $("#header").removeClass("sticky");
        } else {
          $("#header").addClass("sticky");
        }
      });
    }

    //minus
    var buttonPlus  = $(".qty-btn-plus");
    var buttonMinus = $(".qty-btn-minus");

    var incrementPlus = buttonPlus.click(function() {
      var $n = $(this)
      .parent(".qty-container")
      .find(".input-qty");
      $n.val(Number($n.val())+1 );
    });

    var incrementMinus = buttonMinus.click(function() {
      var $n = $(this)
      .parent(".qty-container")
      .find(".input-qty");
      var amount = Number($n.val());
      if (amount > 0) {
        $n.val(amount-1);
      }
    });
    
        // pricing-plan-tab
        $("#ce-toggle").click(function (event) {
          $(".plan-toggle-wrap").toggleClass("active");
        });
    
        $("#ce-toggle").change(function () {
          if ($(this).is(":checked")) {
            $(".tab-content #yearly").hide();
            $(".tab-content #monthly").show();
          } else {
            $(".tab-content #yearly").show();
            $(".tab-content #monthly").hide();
          }
        });

        $(".header-search-btn").on("click", function (e) {
          e.preventDefault();
          $(".header-search-form-wrapper").addClass("open");
          $('.header-search-form-wrapper input[type="search"]').focus();
          $('.body-overlay').addClass('active');
        });
        $(".tx-search-close").on("click", function (e) {
           e.preventDefault();
           $(".header-search-form-wrapper").removeClass("open");
           $("body").removeClass("active");
           $('.body-overlay').removeClass('active');
         });

                //=== logo slider ===
                $('.logo-slider').slick({
                  slidesToShow: 7,
                  slidesToScroll: 1,
                  autoplay: true,
                  autoplaySpeed: 0,
                  speed: 8000,
                  pauseOnHover: true,
                  arrows: false,
                  cssEase: 'linear',

                  responsive: [
                    {
                      breakpoint: 1024,
                      settings: {
                        slidesToShow: 3,
                        slidesToScroll: 3,
                        infinite: true,
                        dots: false
                      }
                    },
                    {
                      breakpoint: 600,
                      settings: {
                        slidesToShow: 2,
                        slidesToScroll: 2
                      }
                    },
                    {
                      breakpoint: 480,
                      settings: {
                        slidesToShow: 2,
                        slidesToScroll: 1
                      }
                    }
                  ]
                });

                $('.all-slider-area').owlCarousel({
                  loop:true,
                  autoplay: true,
                  autoPlayTimeout: 500,
                  margin:10,
                  dots: false,
                  nav: false,
                  responsiveClass:true,
                  responsive:{
                      0:{
                          items:1,
                          nav:true
                      },
                      600:{
                          items:3,
                          nav:false
                      },
                      1000:{
                          items:6,
                          nav:true,
                          loop:false
                      }
                  }
              });

              $('.all-slider-area2').owlCarousel({
                loop:true,
                autoplay: true,
                autoPlayTimeout: 500,
                margin:10,
                dots: false,
                nav: false,
                responsiveClass:true,
                rtl: true,
                responsive:{
                    0:{
                        items:1,
                        nav:true
                    },
                    600:{
                        items:3,
                        nav:false
                    },
                    1000:{
                        items:6,
                        nav:true,
                        loop:false
                    }
                }
            });

                $(".tes2-slider").slick({
                  slidesToShow: 1,
                  slidesToScroll: 1,
                  speed: 1000,
                  dots: false,
                  infinite: true,
                  prevArrow: '.arrow-left',
                  nextArrow: '.arrow-right',
                });

                $(".tes4-slider").slick({
                  slidesToShow: 1,
                  slidesToScroll: 1,
                  loop: true,
                  speed: 1000,
                  dots: false,
                  infinite: true,
                  prevArrow: '.arrow-left4',
                  nextArrow: '.arrow-right4',
                });

              // testimonial 3//
              $('.slider-galeria').slick({
                slidesToShow: 1,
                slidesToScroll: 1,
                arrows: false,
                infinite: false,
                asNavFor: '.slider-galeria-thumbs',
                autoplay: true,
               autoplaySpeed: 2000,
              });
              $('.slider-galeria-thumbs').slick({
                slidesToShow: 3,
                slidesToScroll: 1,
                items:15,
                arrows: false,
                asNavFor: '.slider-galeria',
                vertical: true,
                verticalSwiping: true,
                focusOnSelect: true,
                infinite: false,
                autoplay: true,
                autoplaySpeed: 2000,
              });

               // testimonial 3 rtl//
               $('.slider-galeria2').slick({
                slidesToShow: 1,
                slidesToScroll: 1,
                arrows: false,
                infinite: true,
                autoplay: true,
                autoplaySpeed: 2000,
                rtl: true,
              });

            //service4-slider-all
            $(".service4-slider-all").slick({
              margin: "30",
              slidesToShow: 3,
              arrows: true,
              centerMode: true,
              loop: true,
              centerMode: false,
              prevArrow: $(".service-prev-arrow"),
              nextArrow: $(".service-next-arrow"),
              draggable: true,
              centerPadding: "10px",
              dots: false,
              scroll: true,
              autoplay:true,
              autoplaySpeed:1000,
              responsive: [
                {
                  breakpoint: 769,
                  settings: {
                    arrows: false,
                    centerMode: true,
                    centerPadding: "40px",
                    slidesToShow: 2,
                  },
                },
                {
                  breakpoint: 480,
                  settings: {
                    arrows: false,
                    centerMode: true,
                    centerPadding: "40px",
                    slidesToShow: 1,
                  },
                },
              ],
            });

            //fallery-slider-all
            $(".gallrey-slider").slick({
              margin: "30",
              slidesToShow: 3,
              arrows: true,
              centerMode: true,
              loop: true,
              centerMode: false,
              prevArrow: $(".gallery-prev-arrow"),
              nextArrow: $(".gallery-next-arrow"),
              draggable: true,
              centerPadding: "10px",
              dots: false,
              scroll: true,
              autoplay:true,
              autoplaySpeed:1000,
              responsive: [
                {
                  breakpoint: 769,
                  settings: {
                    arrows: false,
                    centerMode: true,
                    centerPadding: "40px",
                    slidesToShow: 2,
                  },
                },
                {
                  breakpoint: 480,
                  settings: {
                    arrows: false,
                    centerMode: true,
                    centerPadding: "40px",
                    slidesToShow: 1,
                  },
                },
              ],
            });
                  // project style1
                if ($(".project-two__box li").length) {
                  $(".project-two__box li").each(function () {
                    let self = $(this);

                    self.on("mouseenter", function () {
                      console.log($(this));
                      $(".project-two__box li").removeClass("active");
                      $(this).addClass("active");
                    });
                  });
                }

          //Aos animation active
            AOS.init({
              offset: 100,
              duration: 400,
              easing: "ease-in-out",
              anchorPlacement: "top-bottom",
              disable: "mobile",
              once: false,
            });


            //Video poppup
            if ($(".play-btn").length > 0) {
              $(".play-btn").magnificPopup({
                type: "iframe",
              });
            };

              // page-progress
              var progressPath = document.querySelector(".progress-wrap path");
              var pathLength = progressPath.getTotalLength();
              progressPath.style.transition = progressPath.style.WebkitTransition =
                "none";
              progressPath.style.strokeDasharray = pathLength + " " + pathLength;
              progressPath.style.strokeDashoffset = pathLength;
              progressPath.getBoundingClientRect();
              progressPath.style.transition = progressPath.style.WebkitTransition =
                "stroke-dashoffset 10ms linear";
              var updateProgress = function () {
                var scroll = $(window).scrollTop();
                var height = $(document).height() - $(window).height();
                var progress = pathLength - (scroll * pathLength) / height;
                progressPath.style.strokeDashoffset = progress;
              };
              updateProgress();
              $(window).scroll(updateProgress);
              var offset = 50;
              var duration = 550;
              jQuery(window).on("scroll", function () {
                if (jQuery(this).scrollTop() > offset) {
                  jQuery(".progress-wrap").addClass("active-progress");
                } else {
                  jQuery(".progress-wrap").removeClass("active-progress");
                }
              });
              jQuery(".progress-wrap").on("click", function (event) {
                event.preventDefault();
                jQuery("html, body").animate({ scrollTop: 0 }, duration);
                return false;
              });
              



              //product colors
              const colors = $(".accordion1 .accordion-item");
              colors.on("click", function () {
                $(".accordion1 .accordion-item").removeClass("active");
                $(this).addClass("active");
              });

  });


    //preloader
    $(window).on("load", function (event) {
      setTimeout(function () {
        $("#preloader").fadeToggle();
      }, 500);
    });

    	/* Text Effect Animation */
	if ($('.text-anime-style-1').length) {
		let staggerAmount 	= 0.05,
			translateXValue = 0,
			delayValue 		= 0.5,
		   animatedTextElements = document.querySelectorAll('.text-anime-style-1');
		
		animatedTextElements.forEach((element) => {
			let animationSplitText = new SplitText(element, { type: "chars, words" });
				gsap.from(animationSplitText.words, {
				duration: 1,
				delay: delayValue,
				x: 20,
				autoAlpha: 0,
				stagger: staggerAmount,
				scrollTrigger: { trigger: element, start: "top 85%" },
				});
		});		
	}
	
	if ($('.text-anime-style-2').length) {				
		let	 staggerAmount 		= 0.05,
			 translateXValue	= 20,
			 delayValue 		= 0.5,
			 easeType 			= "power2.out",
			 animatedTextElements = document.querySelectorAll('.text-anime-style-2');
		
		animatedTextElements.forEach((element) => {
			let animationSplitText = new SplitText(element, { type: "chars, words" });
				gsap.from(animationSplitText.chars, {
					duration: 1,
					delay: delayValue,
					x: translateXValue,
					autoAlpha: 0,
					stagger: staggerAmount,
					ease: easeType,
					scrollTrigger: { trigger: element, start: "top 85%"},
				});
		});		
	}
	
	if ($('.text-anime-style-3').length) {		
		let	animatedTextElements = document.querySelectorAll('.text-anime-style-3');
		
		 animatedTextElements.forEach((element) => {
			//Reset if needed
			if (element.animation) {
				element.animation.progress(1).kill();
				element.split.revert();
			}

			element.split = new SplitText(element, {
				type: "lines,words,chars",
				linesClass: "split-line",
			});
			gsap.set(element, { perspective: 400 });

			gsap.set(element.split.chars, {
				opacity: 0,
				x: "50",
			});

			element.animation = gsap.to(element.split.chars, {
				scrollTrigger: { trigger: element,	start: "top 95%" },
				x: "0",
				y: "0",
				rotateX: "0",
				opacity: 1,
				duration: 1,
				ease: Back.easeOut,
				stagger: 0.02,
			});
		});		
	}

  $('.hero3-slider-all').owlCarousel({
    items:6,
    center:true,
    autoplay:true,
    autoPlayTimeout:1000,
    autoplaySpeed:3000,
    autoHeight:true,
    autoplayHoverPause:false,
    loop:true,
    // smartSpeed:1000,
    margin:5,
    responsive:{
        300:{
          items:2,
          margin:2
        },

        480:{
          items:4,
          margin:2
        },

        919:{
            items: 3,
            margin:4
        },
        1120:{
          items:6,
          margin:4
      }
    }
  });

  $('.hero-area4').ripples({
    resolution: 512,
    dropRadius: 20,
    perturbance: 0.04,
  });
    

            $('select').niceSelect();


              function animateElements() {
                $('.progressbar').each(function () {
                  var elementPos = $(this).offset().top;
                  var topOfWindow = $(window).scrollTop();
                  var percent = $(this).find('.circle').attr('data-percent');
                  var percentage = parseInt(percent, 10) / parseInt(100, 10);
                  var animate = $(this).data('animate');
                  if (elementPos < topOfWindow + $(window).height() - 10 && !animate) {
                    $(this).data('animate', true);
                    $(this).find('.circle').circleProgress({
                      startAngle: -Math.PI / 2,
                      value: percent / 100,
                      size: 62,
                      thickness: 3,
                      emptyFill: "#D2DEE0",
                      fill: {
                        color: '#2293A7'
                      }
                    }).on('circle-animation-progress', function (event, progress, stepValue) {
                      $(this).find('div').text((stepValue*100).toFixed() + "%");
                    }).stop();
                  }
                });
              }
            
              // Show animated elements
              animateElements();
              $(window).scroll(animateElements);


           //========== CASE IMAGE ============= //
          $('.cs_hover_active').hover(function () {
            $(this).addClass('active').siblings().removeClass('active');
            });

              $('.tes1-slider-all').owlCarousel({
                loop:true,
                margin:10,
                nav: false,
                dots: true,
                responsiveClass:true,
                autoplay: true,
                autoPlayTimeout: 500,
                responsive:{
                    0:{
                        items:1,
                        nav:false
                    },
                    600:{
                        items:1,
                        nav:false
                    },
                    1000:{
                        items:2,
                        nav:false,
                        loop:false
                    }
                }
            });

})(jQuery);