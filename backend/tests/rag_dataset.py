# Each entry: (question, expected_source_filename)
RAG_TEST_CASES = [
    ("What is the return policy for electronics?", "return_policy.txt"),
    ("Can I return clothing if I've worn it?", "return_policy.txt"),
    ("What is the refund approval threshold?", "refund_policy.txt"),
    ("How long do refunds take to process?", "refund_policy.txt"),
    ("How long does standard shipping take?", "shipping_policy.txt"),
    ("Do you ship internationally?", "shipping_policy.txt"),
    ("What should I do if my package shows delivered but I didn't receive it?", "shipping_policy.txt"),
    ("What payment methods are accepted?", "customer_support_faq.txt"),
    ("Can I cancel an order after placing it?", "customer_support_faq.txt"),
    ("What is the warranty period for electronics?", "product_policy.txt"),
]