import streamlit as st
import streamlit.components.v1 as components


def render_business_goal_tab():

    st.title("Business Goal & Analysis Questions")

    st.markdown(
        """
        Rewrite the business goal in your own words and list the questions
        your analysis will answer.
        """
    )

    html = """
<style>
    * {
        box-sizing: border-box;
        font-family: Arial, Helvetica, sans-serif;
    }

    body {
        margin: 0;
        background: transparent;
    }

    /* =====================================================
       PERSON SECTION
       ===================================================== */

    .persona-section {
        margin: 0 0 38px 0;
        padding-bottom: 32px;
        border-bottom: 1px solid #e5e7eb;
    }

    .persona-section:last-child {
        border-bottom: none;
    }

    .persona-header {
        display: flex;
        align-items: center;
        gap: 11px;
        margin-bottom: 16px;
        padding-bottom: 10px;
        border-bottom: 1px solid #eeeeee;
    }

    .persona-avatar {
        width: 38px;
        height: 38px;
        border-radius: 50%;

        display: flex;
        align-items: center;
        justify-content: center;

        background: #f3f4f6;
        color: #374151;

        font-size: 12px;
        font-weight: 700;
        flex-shrink: 0;
    }

    .persona-name {
        font-size: 16px;
        font-weight: 700;
        color: #252525;
    }


    /* =====================================================
       QUESTION GRID
       ===================================================== */

    .question-grid {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 14px;
    }


    /* =====================================================
       STICKY NOTE
       ===================================================== */

    .question-card {
        min-height: 145px;
        padding: 16px;

        background: #fffdf2;

        border: 1px solid #eee8c9;
        border-radius: 6px;

        box-shadow:
            2px 3px 0 rgba(0,0,0,0.03),
            0 5px 12px rgba(0,0,0,0.05);

        transition:
            transform 0.2s ease,
            box-shadow 0.2s ease;
    }

    .question-card:nth-child(2n) {
        background: #fff9e8;
    }

    .question-card:nth-child(3n) {
        background: #fffdf7;
    }

    .question-card:nth-child(4n) {
        background: #fffbea;
    }

    .question-card:hover {
        transform: translateY(-4px);
        box-shadow:
            2px 8px 18px rgba(0,0,0,0.10);
    }

    .question-number {
        font-size: 10px;
        font-weight: 750;
        color: #a18d45;
        margin-bottom: 9px;
    }

    .question-text {
        font-size: 12.5px;
        line-height: 1.5;
        color: #29261d;
    }

    .question-meta {
        margin-top: 11px;
        font-size: 9.5px;
        line-height: 1.4;
        color: #8b856f;
    }


    /* =====================================================
       EMPTY SPACE
       ===================================================== */

    .empty-note {
        min-height: 120px;

        display: flex;
        align-items: center;
        justify-content: center;

        border: 1px dashed #d8d2b8;
        background: #fffef8;

        color: #aaa38d;
        font-size: 12px;

        border-radius: 6px;
    }


    /* =====================================================
       RESPONSIVE
       ===================================================== */

    @media (max-width: 1100px) {
        .question-grid {
            grid-template-columns: repeat(3, 1fr);
        }
    }

    @media (max-width: 800px) {
        .question-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    @media (max-width: 550px) {
        .question-grid {
            grid-template-columns: 1fr;
        }
    }

</style>
"""

    html += """


    <!-- SAHIB -->

    <div class="persona-section">

        <div class="persona-header">
            <div class="persona-avatar">SR</div>
            <div class="persona-name">Sahib Randhawa</div>
        </div>

        <div class="question-grid">

            <div class="empty-note">
                Add questions here
            </div>

        </div>

    </div>


    <!-- YASH -->

    <div class="persona-section">

        <div class="persona-header">
            <div class="persona-avatar">YA</div>
            <div class="persona-name">Yash Arabhavi</div>
        </div>

        <div class="question-grid">

            <div class="question-card">
                <div class="question-text">
                    <a href="https://claude.ai/code/artifact/441d83fb-d88a-4d77-a663-4cdd2f0f886e" target="_blank">https://claude.ai/code/artifact/441d83fb-d88a-4d77-a663-4cdd2f0f886e</a>
                </div>
                
            </div>

            <div class="question-card">
                <div class="question-number">Q1 · P1</div>
                <div class="question-text">
                    How strongly does delivery lateness predict a bad review,
                    and where is the cliff edge? <i>Is the relationship linear,
                    or does satisfaction collapse past a threshold?</i>
                </div>
                <div class="question-meta">
                    orders + order_reviews · delay_vs_promise · review_score
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q2 · P1</div>
                <div class="question-text">
                    Is it <b>being slow</b> or <b>breaking the promise</b>
                    that angers customers? An order delivered in 20 days but
                    5 days early vs one delivered in 8 days but 2 days late,
                    which scores worse?
                </div>
                <div class="question-meta">
                    orders + order_reviews · delivery_days · delay_vs_promise
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q3 · P2</div>
                <div class="question-text">
                    Does padding the delivery estimate buy goodwill, or does
                    a long quoted wait suppress satisfaction before the order
                    even ships?
                </div>
                <div class="question-meta">
                    promise_buffer · review_score
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q4 · P2</div>
                <div class="question-text">
                    Beyond delivery, what else moves the score — price,
                    freight ratio, product weight/size, photo count,
                    description length, number of items?
                </div>
                <div class="question-meta">
                    order_items + products + order_reviews
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q5 · P1</div>
                <div class="question-text">
                    Which product categories carry high revenue
                    <b>and</b> poor satisfaction?
                </div>
                <div class="question-meta">
                    Revenue · negative-review rate · order volume
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q6 · P1</div>
                <div class="question-text">
                    How concentrated is the damage across sellers?
                    What share of all 1★ reviews comes from the worst
                    5% of sellers?
                </div>
                <div class="question-meta">
                    order_items + sellers + order_reviews
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q7 · P2</div>
                <div class="question-text">
                    Which seller-state → customer-state routes perform worst?
                    Is poor delivery about <b>distance</b>, or about specific
                    bad <b>origins</b>?
                </div>
                <div class="question-meta">
                    geolocation · seller state · customer state
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q8 · P1</div>
                <div class="question-text">
                    Which seller behaviours predict bad reviews — handling
                    time, order volume, catalogue breadth, freight pricing?
                </div>
                <div class="question-meta">
                    orders + order_items + sellers
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q9 · P2</div>
                <div class="question-text">
                    Do newly-onboarded and low-volume sellers underperform
                    established ones?
                </div>
                <div class="question-meta">
                    Seller cohorts · first-sale month
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q10 · P1</div>
                <div class="question-text">
                    If the marketplace removed the worst-performing X% of
                    sellers, how much GMV is lost and how much does the
                    negative-review rate improve?
                </div>
                <div class="question-meta">
                    Trade-off curve · GMV · negative-review rate
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q11 · P2</div>
                <div class="question-text">
                    Which categories are growing fastest, and is their
                    satisfaction holding or degrading as they scale?
                </div>
                <div class="question-meta">
                    2017-01 → 2018-08
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q12 · P2</div>
                <div class="question-text">
                    Do acquisition channel, lead type, or business segment
                    predict how good a seller turns out to be?
                </div>
                <div class="question-meta">
                    mql + closed_deals + performance
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q13 · P2</div>
                <div class="question-text">
                    Do multi-item or multi-seller orders score worse
                    (split-shipment risk)?
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q14 · P2</div>
                <div class="question-text">
                    Do payment type and installment count relate to
                    satisfaction or cancellation?
                </div>
            </div>

        </div>

    </div>


    <!-- KANNAN -->

    <div class="persona-section">

        <div class="persona-header">
            <div class="persona-avatar">KS</div>
            <div class="persona-name">Kannan S</div>
        </div>

        <div class="question-grid">

            <div class="question-card">
                <div class="question-number">Q1</div>
                <div class="question-text">
                    What is the relationship between delivery delay
                    (actual vs estimated date) and review score?
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q2</div>
                <div class="question-text">
                    How much of the total delivery time comes from seller
                    handling (purchase -> carrier) vs carrier transit
                    (carrier -> customer)? Which stage should be optimized first?
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q3</div>
                <div class="question-text">
                    Does freight cost as a % of order value have any
                    relationship with delivery delay or review score?
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q4</div>
                <div class="question-text">
                    Does interstate vs intrastate shipping
                    (seller state ≠ customer state) affect delivery delay
                    and customer satisfaction?
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q5</div>
                <div class="question-text">
                    Among sellers with a minimum order volume (e.g >=5 orders),
                    which sellers have the highest late-delivery rates and
                    lowest review scores? Also, what share of total GMV
                    (Gross Merchandise Value) do these "risk sellers" represent?
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q6</div>
                <div class="question-text">
                    Which product categories have the best and worst
                    average review scores?
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q7</div>
                <div class="question-text">
                    Do product characteristics such as weight, dimensions,
                    and number of product photos have any relationship
                    with review scores?
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q8</div>
                <div class="question-text">
                    Which customer states consistently have worse delivery
                    performance and customer satisfaction?
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q9</div>
                <div class="question-text">
                    Is there a pattern between specific seller-state ->
                    customer-state shipping pairs and delivery delays/satisfaction?
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q10</div>
                <div class="question-text">
                    Does payment type or number of installments have any
                    relationship with order value, delivery delay,
                    or review score?
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q11</div>
                <div class="question-text">
                    Out of all these factors — delivery delay, freight %,
                    category, seller, region, and payment — which ones have
                    the strongest relationship with review score?
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q12</div>
                <div class="question-text">
                    What does the "path to a 1-star review" look like?
                    In other words, what percentage of low review scores
                    can be explained by late delivery versus other factors?
                </div>
            </div>

        </div>

    </div>


    <!-- ASHWANTH -->

        <!-- ASHWANTH -->

    <div class="persona-section">

        <div class="persona-header">
            <div class="persona-avatar">AV</div>
            <div class="persona-name">Ashwanth V</div>
        </div>

        <div class="question-grid">

            <div class="question-card">
                <div class="question-number">Q1</div>
                <div class="question-text">
                    What overall share of orders result in an unhappy customer
                    (1–2 star review), and has that share been rising or falling
                    over time?
                </div>
                <div class="question-meta">
                    order_reviews · orders · review_score · purchase_timestamp
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q2</div>
                <div class="question-text">
                    How much of customer dissatisfaction is explained by late
                    delivery, versus something else entirely such as product
                    quality or seller behavior?
                </div>
                <div class="question-meta">
                    delivery dates · estimated delivery · review_score
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q3</div>
                <div class="question-text">
                    Which product categories generate the most growth
                    (order/revenue volume) while carrying the most
                    dissatisfaction risk?
                </div>
                <div class="question-meta">
                    order_items · products · categories · reviews
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q4</div>
                <div class="question-text">
                    Are certain sellers a recurring source of bad experiences
                    regardless of category or delivery time, and how much of
                    total marketplace volume do they represent?
                </div>
                <div class="question-meta">
                    seller_id · order volume · review_score
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q5</div>
                <div class="question-text">
                    Is dissatisfaction a broad, platform-wide problem, or is it
                    concentrated in a small number of sellers, categories, or
                    regions that could be targeted directly?
                </div>
                <div class="question-meta">
                    seller · category · region · dissatisfaction concentration
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q6</div>
                <div class="question-text">
                    Do certain regions of the country experience systematically
                    worse delivery performance and satisfaction, independent
                    of which sellers serve them?
                </div>
                <div class="question-meta">
                    customer_state · seller_state · delivery delay · reviews
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q7</div>
                <div class="question-text">
                    Where in the order journey does the delay actually happen:
                    seller handling/dispatch or carrier transit, and which leg
                    matters more for customer satisfaction?
                </div>
                <div class="question-meta">
                    purchase → carrier · carrier → customer · review_score
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q8</div>
                <div class="question-text">
                    Do higher-cost orders, higher shipping costs relative to
                    price, or long installment plans make customers more likely
                    to leave a bad review?
                </div>
                <div class="question-meta">
                    payments · price · freight_value · installments · reviews
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q9</div>
                <div class="question-text">
                    Does the way a seller was acquired, such as lead source,
                    business segment, or declared revenue at onboarding,
                    predict whether they become a high-risk seller later?
                </div>
                <div class="question-meta">
                    closed_deals · marketing_leads · seller performance
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q10</div>
                <div class="question-text">
                    If leadership had to choose where to invest, such as
                    support and incentives, versus where to intervene through
                    enforcement or offboarding, which seller, category, or
                    region segments would improve satisfaction most without
                    shrinking the catalogue?
                </div>
                <div class="question-meta">
                    Q3–Q7 synthesis · risk vs volume · intervention priorities
                </div>
            </div>

        </div>

    </div>


    <!-- ANUSHKA -->

        <!-- ANUSHKA -->

    <div class="persona-section">

        <div class="persona-header">
            <div class="persona-avatar">A</div>
            <div class="persona-name">Anushka</div>
        </div>

        <div class="question-grid">

            <div class="question-card">
                <div class="question-number">Q1</div>
                <div class="question-text">
                    How does delivery delay affect customer review scores?
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q2</div>
                <div class="question-text">
                    Which product categories receive the highest and lowest
                    customer ratings?
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q3</div>
                <div class="question-text">
                    Which seller behaviors (shipping speed, order handling
                    time, cancellations) are linked to poor reviews?
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q4</div>
                <div class="question-text">
                    Which regions have the most late deliveries and
                    dissatisfied customers?
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q5</div>
                <div class="question-text">
                    Does payment method or installment usage influence
                    customer satisfaction?
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q6</div>
                <div class="question-text">
                    How do freight cost and delivery distance relate to
                    delivery performance?
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q7</div>
                <div class="question-text">
                    Which sellers consistently perform well or poorly?
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q8</div>
                <div class="question-text">
                    What characteristics distinguish 5-star orders from
                    1-star orders?
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q9</div>
                <div class="question-text">
                    Are there seasonal periods when delays and negative
                    reviews increase?
                </div>
            </div>

            <div class="question-card">
                <div class="question-number">Q10</div>
                <div class="question-text">
                    Where should the company invest (logistics, sellers,
                    or regions) to maximize growth while preserving
                    customer satisfaction?
                </div>
            </div>

        </div>

    </div>
    """

    components.html(
        html,
        height=2600,
        scrolling=False
    )