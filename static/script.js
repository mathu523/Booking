// =========================================
// GET ELEMENTS
// =========================================

const bookingForm =
    document.getElementById("bookingForm");

const submitBtn =
    document.getElementById("submitBtn");

const buttonText =
    document.getElementById("buttonText");

const message =
    document.getElementById("message");


// =========================================
// FORM SUBMIT
// =========================================

bookingForm.addEventListener(
    "submit",
    async function (event) {

        // Prevent page refresh
        event.preventDefault();


        // =====================================
        // GET FORM VALUES
        // =====================================

        const customerName =
            document
                .getElementById("customerName")
                .value
                .trim();


        const phone =
            document
                .getElementById("phone")
                .value
                .trim();


        const service =
            document
                .getElementById("service")
                .value;


        const amount =
            document
                .getElementById("amount")
                .value
                .trim();


        const payment =
            document.querySelector(
                'input[name="payment"]:checked'
            )?.value;


        // =====================================
        // VALIDATION
        // =====================================

        if (!customerName) {

            showMessage(
                "Please enter customer name.",
                "error"
            );

            return;
        }


        if (!/^[0-9]{10}$/.test(phone)) {

            showMessage(
                "Please enter a valid 10-digit phone number.",
                "error"
            );

            return;
        }


        if (!service) {

            showMessage(
                "Please select a service.",
                "error"
            );

            return;
        }


        if (
            !amount ||
            Number(amount) <= 0
        ) {

            showMessage(
                "Please enter a valid amount.",
                "error"
            );

            return;
        }


        if (!payment) {

            showMessage(
                "Please select payment method.",
                "error"
            );

            return;
        }


        // =====================================
        // BOOKING DATA
        // =====================================

        const bookingData = {

            customer_name: customerName,

            phone: phone,

            service: service,

            amount: amount,

            payment_method: payment

        };


        // =====================================
        // SEND DATA TO FLASK
        // =====================================

        try {

            submitBtn.disabled = true;

            buttonText.textContent =
                "Saving...";


            const response =
                await fetch(
                    "/book",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                bookingData
                            )
                    }
                );


            const result =
                await response.json();


            // =================================
            // SUCCESS
            // =================================

            if (response.ok) {

                showMessage(
                    result.message,
                    "success"
                );


                // Clear form
                bookingForm.reset();

            }


            // =================================
            // ERROR
            // =================================

            else {

                showMessage(
                    result.message ||
                    "Unable to save booking.",
                    "error"
                );

            }

        }


        // =====================================
        // CONNECTION ERROR
        // =====================================

        catch (error) {

            console.error(
                "Server Error:",
                error
            );


            showMessage(
                "Unable to connect to server.",
                "error"
            );

        }


        // =====================================
        // ENABLE BUTTON
        // =====================================

        finally {

            submitBtn.disabled = false;

            buttonText.textContent =
                "Submit Booking";

        }

    }
);


// =========================================
// SHOW MESSAGE
// =========================================

function showMessage(
    text,
    type
) {

    message.textContent = text;

    message.className =
        "message " + type;

}