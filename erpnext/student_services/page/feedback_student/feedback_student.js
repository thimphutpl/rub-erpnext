frappe.pages['feedback-student'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Feedback Forms',
        single_column: true
    });
    
    var style = document.createElement('style');
    style.innerHTML = `
        .page-title .title-text {
            text-align: center !important;
            width: 100% !important;
            color: #055cfc !important;
            font-size: 24px !important;
            font-weight: bold !important;
        }
        .page-head {
            background-color: #f8f9fa !important;
            border-bottom: 2px solid #2c07f8 !important;
        }
        .page-title {
            display: flex !important;
            justify-content: center !important;
            width: 100% !important;
        }
        
        #feedback-type {
            width: 100% !important;
            min-height: 38px !important;
            background-color: white !important;
            border: 1px solid #d1d8dd !important;
            border-radius: 4px !important;
            padding: 8px 12px !important;
        }
        
        .rating-section {
            margin-top: 30px;
            border-top: 2px solid #055cfc;
            padding-top: 20px;
        }
        
        .rating-question-card {
            background: #f8f9fa;
            border: 1px solid #e1e9f0;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .question-title {
            font-size: 16px;
            font-weight: 600;
            color: #055cfc;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px dashed #d1d8dd;
        }
        
        .rating-container {
            display: flex;
            flex-direction: row;
            justify-content: space-around;
            align-items: center;
            gap: 10px;
            margin: 15px 0;
            padding: 10px;
            background: white;
            border-radius: 6px;
        }
        
        .rating-option {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 5px;
            flex: 1;
        }
        
        .rating-option input[type="radio"] {
            width: 20px;
            height: 20px;
            cursor: pointer;
        }
        
        .rating-option label {
            font-size: 14px;
            color: #555;
            cursor: pointer;
            font-weight: 500;
        }
        
        .rating-label {
            text-align: center;
            font-size: 12px;
            color: #777;
        }
        
        .rating-scale {
            display: flex;
            justify-content: space-between;
            margin-top: 5px;
            padding: 0 10px;
            font-size: 12px;
            color: #888;
        }
        
        .oeq-section {
            margin-top: 30px;
            border-top: 2px solid #055cfc;
            padding-top: 20px;
        }
        
        .oeq-question-card {
            background: #f8f9fa;
            border: 1px solid #e1e9f0;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .oeq-textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid #d1d8dd;
            border-radius: 4px;
            resize: vertical;
            font-family: inherit;
            margin-top: 10px;
        }
        
        .section-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .section-header h3 {
            margin: 0;
            color: #333;
        }
        
        .section-icon {
            font-size: 24px;
        }
        
        .alert-info {
            background-color: #d9edf7;
            border: 1px solid #bce8f1;
            color: #31708f;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        
        .alert-warning {
            background-color: #fcf8e3;
            border: 1px solid #faebcc;
            color: #8a6d3b;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        
        .disabled-input {
            opacity: 0.7;
            pointer-events: none;
        }
    `;
    document.head.appendChild(style);
    
    $(wrapper).find('.page-content').empty();
    
    $(wrapper).find('.page-content').append(`
        <div class="feedback-form-container" style="max-width: 900px; margin: 30px auto; padding: 20px;">
            <div class="feedback-form-card" style="background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 30px;">
                
                <div class="form-group">
                    <label for="feedback-type" style="font-weight: 600; margin-bottom: 8px; display: block; color: #333;">
                        Feedback Type <span style="color: red;">*</span>
                    </label>
                    <select id="feedback-type" class="form-control">
                        <option value="">Select Feedback Type</option>
                    </select>
                </div>
                
                <div id="feedback-status" style="display: none;"></div>
                
                <div id="questions-container" style="display: none;">
                    <div id="rating-section" class="rating-section" style="display: none;">
                        <div class="section-header">
                            <span class="section-icon">⭐</span>
                            <h3>Rating Questions</h3>
                        </div>
                        <div id="rating-questions"></div>
                    </div>
                    
                    <div id="oeq-section" class="oeq-section" style="display: none;">
                        <div class="section-header">
                            <span class="section-icon">✏️</span>
                            <h3>Open Ended Questions</h3>
                        </div>
                        <div id="oeq-questions"></div>
                    </div>
                </div>
                
                <div style="text-align: right; margin-top: 30px;">
                    <button id="submit-feedback" class="btn btn-primary" style="padding: 10px 30px; font-size: 14px;">
                        Submit Feedback
                    </button>
                </div>
            </div>
        </div>
    `);
    
    load_feedback_types(wrapper);
    
    $(wrapper).find('#feedback-type').on('change', function() {
        var selected_value = $(this).val();
        if (selected_value) {
            load_feedback_data(wrapper, selected_value);
        } else {
            $(wrapper).find('#questions-container').hide();
            $(wrapper).find('#feedback-status').hide().empty();
            $(wrapper).find('#submit-feedback').show();
            $(wrapper).find('#rating-questions').empty();
            $(wrapper).find('#oeq-questions').empty();
        }
    });
    
    $(wrapper).find('#submit-feedback').click(function() {
        submit_feedback(wrapper);
    });
}

function load_feedback_types(wrapper) {
    frappe.call({
        method: 'erpnext.student_services.page.feedback_student.feedback_student.get_feedback_type',
        callback: function(response) {
            if (response.message && response.message.length > 0) {
                var select = $(wrapper).find('#feedback-type');
                select.find('option:not(:first)').remove();
                
                response.message.forEach(function(item) {
                    select.append(`<option value="${item.name}">${item.name}</option>`);
                });
            }
        },
        error: function(err) {
            frappe.msgprint(__('Error loading feedback types.'));
        }
    });
}

function load_feedback_data(wrapper, feedback_type) {
    var ratingContainer = $(wrapper).find('#rating-questions');
    var oeqContainer = $(wrapper).find('#oeq-questions');
    var statusDiv = $(wrapper).find('#feedback-status');
    var submitBtn = $(wrapper).find('#submit-feedback');
    
    ratingContainer.empty();
    oeqContainer.empty();
    $(wrapper).find('#rating-section').hide();
    $(wrapper).find('#oeq-section').hide();
    $(wrapper).find('#questions-container').hide();
    statusDiv.hide().empty().removeClass();
    submitBtn.show().prop('disabled', false);
    
    frappe.call({
        method: 'erpnext.student_services.page.feedback_student.feedback_student.get_feedback_data',
        args: {
            feedback_type: feedback_type,
            student: frappe.session.user
        },
        callback: function(response) {
            if (response.message) {
                var data = response.message;
                
                if (!data.has_questions) {
                    statusDiv.addClass('alert-warning')
                        .html('<strong>No Questions:</strong> No questions have been set up for this feedback type.')
                        .show();
                    submitBtn.hide();
                    return;
                }
                
                var hasRatingQuestions = data.rating_questions && data.rating_questions.length > 0;
                var hasOEQQuestions = data.oeq_questions && data.oeq_questions.length > 0;
                
                if (!hasRatingQuestions && !hasOEQQuestions) {
                    statusDiv.addClass('alert-warning')
                        .html('<strong>No Questions Configured:</strong> Please contact administrator.')
                        .show();
                    submitBtn.hide();
                    return;
                }
                
                if (hasRatingQuestions) {
                    displayRatingQuestions(wrapper, data.rating_questions);
                    $(wrapper).find('#rating-section').show();
                }
                
                if (hasOEQQuestions) {
                    displayOEQQuestions(wrapper, data.oeq_questions);
                    $(wrapper).find('#oeq-section').show();
                }
                
                $(wrapper).find('#questions-container').show();
                
                // Check if feedback already exists
                if (data.existing_feedback && data.existing_feedback.name) {
                    // statusDiv.addClass('alert-info')
                    //     .html(`<strong>Already Submitted:</strong> You submitted feedback on ${formatDate(data.existing_feedback.creation)}.`)
                    //     .show();
                    populateExistingResponses(wrapper, data.existing_feedback);
                    $(wrapper).find('input[type="radio"], textarea').prop('disabled', true);
                    submitBtn.hide();
                }
            }
        },
        error: function(err) {
            frappe.msgprint(__('Error loading feedback data.'));
        }
    });
}

function displayRatingQuestions(wrapper, rating_questions) {
    var ratingContainer = $(wrapper).find('#rating-questions');
    var ratingDescriptions = ['Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree'];
    
    rating_questions.forEach(function(question, qIndex) {
        var questionHtml = `
            <div class="rating-question-card" data-question="${question.question}">
                <div class="question-title">
                    <strong>Q${qIndex + 1}.</strong> ${question.question}
                </div>
                <div class="rating-scale">
                    <span>Strongly Disagree</span>
                    <span>Strongly Agree</span>
                </div>
                <div class="rating-container">
        `;
        
        for (var i = 1; i <= 5; i++) {
            questionHtml += `
                <div class="rating-option">
                    <input type="radio" 
                           name="rating_${qIndex}" 
                           value="${i}"
                           data-question="${question.question}">
                    <label>${i}</label>
                    <div class="rating-label">${ratingDescriptions[i-1]}</div>
                </div>
            `;
        }
        
        questionHtml += `</div></div>`;
        ratingContainer.append(questionHtml);
    });
}

function displayOEQQuestions(wrapper, oeq_questions) {
    var oeqContainer = $(wrapper).find('#oeq-questions');
    
    oeq_questions.forEach(function(question, qIndex) {
        var questionHtml = `
            <div class="oeq-question-card">
                <div class="question-title">
                    <strong>Q${qIndex + 1}.</strong> ${question.question}
                </div>
                <div class="form-group">
                    <textarea 
                        class="oeq-textarea" 
                        rows="4"
                        placeholder="Please enter your answer here..."
                        data-question="${question.question}"></textarea>
                </div>
            </div>
        `;
        
        oeqContainer.append(questionHtml);
    });
}

function populateExistingResponses(wrapper, existing) {
    if (existing.rating_responses && existing.rating_responses.length > 0) {
        existing.rating_responses.forEach(function(resp) {
            $(wrapper).find(`input[type="radio"][data-question="${resp.question}"][value="${resp.rating}"]`).prop('checked', true);
        });
    }
    
    if (existing.oeq_responses && existing.oeq_responses.length > 0) {
        existing.oeq_responses.forEach(function(resp) {
            $(wrapper).find(`textarea[data-question="${resp.question}"]`).val(resp.response_text);
        });
    }
}

function submit_feedback(wrapper) {
    var feedback_type = $(wrapper).find('#feedback-type').val();
    
    if (!feedback_type) {
        frappe.msgprint(__('Please select a feedback type'));
        return;
    }
    
    var rating_answers = [];
    var allRated = true;
    $(wrapper).find('.rating-question-card').each(function() {
        var question = $(this).data('question');
        var selectedRating = $(this).find('input[type="radio"]:checked');
        
        if (selectedRating.length > 0) {
            rating_answers.push({
                question: question,
                rating: selectedRating.val()
            });
        } else {
            allRated = false;
        }
    });
    
    if ($(wrapper).find('.rating-question-card').length > 0 && !allRated) {
        frappe.msgprint(__('Please answer all rating questions'));
        return;
    }
    
    var oeq_answers = [];
    $(wrapper).find('.oeq-question-card').each(function() {
        var textarea = $(this).find('textarea');
        var answer = textarea.val().trim();
        
        if (answer) {
            oeq_answers.push({
                question: textarea.data('question'),
                answer: answer
            });
        }
    });
    
    if (rating_answers.length === 0 && oeq_answers.length === 0) {
        frappe.msgprint(__('Please answer at least one question'));
        return;
    }
    
    var submitBtn = $(wrapper).find('#submit-feedback');
    submitBtn.prop('disabled', true).html('Submitting...');
    
    frappe.call({
        method: 'erpnext.student_services.page.feedback_student.feedback_student.submit_feedback_responses',
        args: {
            feedback_type: feedback_type,
            rating_answers: rating_answers,
            oeq_answers: oeq_answers,
            student: frappe.session.user
        },
        callback: function(response) {
            if (response.message && response.message.success) {
                frappe.show_alert({
                    message: 'Feedback submitted successfully!',
                    indicator: 'green'
                }, 3);
                load_feedback_data(wrapper, feedback_type);
            } else if (response.message && response.message.error) {
                frappe.msgprint(response.message.error);
                submitBtn.prop('disabled', false).html('Submit Feedback');
            } else {
                frappe.msgprint(__('Error submitting feedback.'));
                submitBtn.prop('disabled', false).html('Submit Feedback');
            }
        },
        error: function(err) {
            frappe.msgprint(__('Error submitting feedback.'));
            submitBtn.prop('disabled', false).html('Submit Feedback');
        }
    });
}

function formatDate(date_str) {
    var date = new Date(date_str);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}