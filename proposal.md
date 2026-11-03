# Capstone Proposal: ReviewPulse

## Problem and target user
Small online sellers often receive more customer reviews than they can read one by one. ReviewPulse will help a seller quickly understand the overall tone of a batch of reviews and spot individual reviews that may need attention.

## Product
ReviewPulse is a local web app. A user can enter one review or upload a CSV of reviews. The app predicts positive, neutral, or negative sentiment, shows a confidence score, and summarizes the sentiment distribution for the uploaded batch.

## Skills and technology
The project combines two skills from Weeks 1–7: classical NLP classification and building a user-facing Streamlit application. The classifier will use scikit-learn TF-IDF features and Logistic Regression, trained on a real labeled review dataset. The app will run locally and use the saved classifier; it will not call an external AI API.

## Success criteria
1. Use at least 1,000 real, labeled review examples and save a reproducible train/validation/test split with a fixed seed.
2. Train and evaluate the classifier; report precision, recall, and F1 for each class, plus macro F1 and the class distribution.
3. Let a user classify one review and upload a CSV for batch analysis; display predictions, confidence scores, and a sentiment summary.
4. Demonstrate the complete app live, and provide setup instructions so a mentor can run it locally.

## Scope and evaluation
The first version will focus on three-class review sentiment and a clear local demo. I will prioritize data quality, evaluation, and reliable setup. Public deployment, transformer models, user accounts, and external APIs are out of scope. I will report the actual results, limitations, and any criteria that are not met.

## Approval
Approved by mentor before implementation. Development began after approval.
