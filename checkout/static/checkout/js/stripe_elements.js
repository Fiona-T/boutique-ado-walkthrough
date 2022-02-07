/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment
    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

// get the text from the script elements, and stlice off the quotation marks
const stripePublicKey = $('#id_stripe_public_key').text().slice(1, -1);
const clientSecret = $('#id_client_secret').text().slice(1, -1);
// stripe public key
const stripe = Stripe(stripePublicKey);
// create instance of stripe elements
const elements = stripe.elements();
const style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': {
            color: '#aab7c4'
        }
    },
    invalid: {
        color: '#dc3545',
        iconColor: '#dc3545'
    }
};
// create a card element (in stripe docs referred to as paymentElement)
const card = elements.create('card', {style: style});
// mount the card element to the div in the checkout.html file
card.mount('#card-element');

// handle realtime validation errors on the card element
card.addEventListener('change', function(event) {
    let errorDiv = document.getElementById('card-errors');
    // if there's an error, display it in error div
    if (event.error) {
        let html = `
        <span class="icon" role="alert">
            <i class="fas fa-times"></i>
        </span>
        <span>${event.error.message}</span>
        `;
        $(errorDiv).html(html);
    } else {
        errorDiv.textContent = '';
    }
});

// Handle form submit
const form = document.getElementById('payment-form');

form.addEventListener('submit', function(ev) {
    ev.preventDefault();
    // disable card element and submit btn to prevent multiple submissions
    card.update({ 'disabled': true});
    $('#submit-button').attr('disabled', true);
    // fade out the form and trigger the overlay
    $('#payment-form').fadeToggle(100);
    $('#loading-overlay').fadeToggle(100);

    // get Boolean value of savinfo box by looking at its checked attribute
    let saveInfo = Boolean($('#id-save-info').attr('checked'));
    // Get value of csrf token from using {% csrf_token %} in the form
    let csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
    // pass this info to the view, as well as the client secret for payment intent
    let postData = {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': clientSecret,
        'save_info': saveInfo,
    };
    // the url for cache checkout view
    let url = '/checkout/cache_checkout_data/';
    // post the postData to the view, using the url
    // wait for a response that payment intent was updated before calling confirmCardPayment
    // using the .done method, and executing the callback function - i.e. if the view returns 200 status
    $.post(url, postData).done(function() {
        // the stripe.confrimCardPayment method will go in here
        // call confirm card payment method, providing the card to stripe, then execute
        // the function on the result
        stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                // data from the form - to add the form data to the payment intent object
                billing_details: {
                    name: $.trim(form.full_name.value),
                    phone: $.trim(form.phone_number.value),
                    email: $.trim(form.email.value),
                    address:{
                        line1: $.trim(form.street_address1.value),
                        line2: $.trim(form.street_address2.value),
                        city: $.trim(form.town_or_city.value),
                        country: $.trim(form.country.value),
                        state: $.trim(form.county.value),
                    }
                }
            },
            shipping: {
                name: $.trim(form.full_name.value),
                phone: $.trim(form.phone_number.value),
                address: {
                    line1: $.trim(form.street_address1.value),
                    line2: $.trim(form.street_address2.value),
                    city: $.trim(form.town_or_city.value),
                    country: $.trim(form.country.value),
                    postal_code: $.trim(form.postcode.value),
                    state: $.trim(form.county.value),
                }
            },
        }).then(function(result) {
            if (result.error) {
                let errorDiv = document.getElementById('card-errors');
                let html = `
                    <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                    </span>
                    <span>${result.error.message}</span>`;
                $(errorDiv).html(html);
                // fade in the form again and remove overlay so errors can be fixed
                $('#payment-form').fadeToggle(100);
                $('#loading-overlay').fadeToggle(100);
                // re-enable the card element and the submit btn so error can be fixed
                card.update({ 'disabled': false});
                $('#submit-button').attr('disabled', false);
            } else {
                // payment successful, submit the form (prevented above)
                if (result.paymentIntent.status === 'succeeded') {
                    form.submit();
                }
            }
        });
    }).fail(function() {
        // fail response if view returns 400 response
        // just reload the page, the error will be in django messages returned by view
        location.reload();
    })
});