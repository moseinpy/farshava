/*code range*/

 $('#sl2').slider();

	var RGBChange = function() {
	  $('#RGB').css('background', 'rgb('+r.getValue()+','+g.getValue()+','+b.getValue()+')')
	};	
		
/*scroll to top*/

$(document).ready(function(){
	$(function () {
		$.scrollUp({
	        scrollName: 'scrollUp', // Element ID
	        scrollDistance: 300, // Distance from top/bottom before showing element (px)
	        scrollFrom: 'top', // 'top' or 'bottom'
	        scrollSpeed: 300, // Speed back to top (ms)
	        easingType: 'linear', // Scroll to top easing (see http://easings.net/)
	        animation: 'fade', // Fade, slide, none
	        animationSpeed: 200, // Animation in speed (ms)
	        scrollTrigger: false, // Set a custom triggering element. Can be an HTML string or jQuery object
					//scrollTarget: false, // Set a custom target element for scrolling to the top
	        scrollText: '<i class="fa fa-angle-up"></i>', // Text for element, can contain HTML
	        scrollTitle: false, // Set a custom <a> title if required.
	        scrollImg: false, // Set true to use image
	        activeOverlay: false, // Set CSS color to display scrollUp active point, e.g '#00FFFF'
	        zIndex: 2147483647 // Z-Index for the overlay
		});
	});
});




function updateCode(container, n) {
   //container -> each one of the $('.cd-gallery').children('li')
   //n -> index of the selected item in the .cd-item-wrapper
   var codeTag = container.find('.cd-code'),
       selectedItem = container.find('.cd-item-wrapper li').eq(n);
   if( selectedItem.data('sale') ) { 
      // if item is on sale - cross old code and add new one
      codeTag.addClass('on-sale');
      var newCodeTag = ( codeTag.next('.cd-new-code').length > 0 ) ? codeTag.next('.cd-new-code') : $('<em class="cd-new-code"></em>').insertAfter(codeTag);
      newCodeTag.text(selectedItem.data('code'));
      setTimeout(function(){ newCodeTag.addClass('is-visible'); }, 100);
   } else {
      // if item is not on sale - remove cross on old code and sale code
      codeTag.removeClass('on-sale').next('.cd-new-code').removeClass('is-visible').on('webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend', function(){
         codeTag.next('.cd-new-code').remove();
      });
   }
}