console.log('Script loaded');
// on the home page, we have this <li class="single-item cart-area" id="cart-offcanvas"><a class="single-btn cart-btn" data-bs-toggle="offcanvas" href="#cartOffcanvasSidebar" aria-controls="cartOffcanvasSidebar"><i class="btn-icon flaticon-shopping-bag"></i></a></li> tag that triggers the cart offcanvas sidebar when clicked. Add a function that clicks the cart button and opens the cart offcanvas sidebar.
function openCartOffcanvas() {
    document.querySelector('.cart-btn').click();
}
// add a document ready function to the page


function AjaxAddToCart(event, addToCartUrl, slug) {
    event.preventDefault();
    $.ajax({
        type: "POST",
        url: addToCartUrl,
        data: {
            slug: slug,
            quantity: 1,
            csrfmiddlewaretoken: document.querySelector('[name=csrfmiddlewaretoken]').value,
            datatype: 'json',
        },
        success: function (data) {
            console.log(data);
            openCartOffcanvas();
            // reload the div with an id of total-bottom-part
            $('#total-bottom-part').load(location.href + ' #total-bottom-part');
            // reload the div with an id of disabled-total-bottom-part
            $('#disabled-total-bottom-part').load(location.href + ' #disabled-total-bottom-part');
            // reload the div with an id of total-bottom-body
            $('#total-bottom-body').load(location.href + ' #total-bottom-body');
            $('#total-bottom').load(location.href+" #total-bottom>*","");
            $('#total-div').load(location.href+" #total-div>*","");
            $('#cart-product-list').load(location.href+" #cart-product-list>*","");
            $('#price-area').load(location.href+" #price-area>*","");
            $('#cart-items').load(location.href+" #cart-items>*","");
            $('#cart-total').load(location.href+" #cart-total>*","");

            

        },
        error: function (data) {
            console.log(data);
            console.log('Does not work');
        }
    })
};