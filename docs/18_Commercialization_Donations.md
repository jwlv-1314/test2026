# 18. Commercialization & Donations

### 18.1 Donation Feature

#### 18.1.1 Feature Overview

To support developers in the ongoing maintenance and development of quality applications, the TNAS Developer Platform provides the ability to configure donation links. Developers can add a donation link in their personal profile, and a donation button will automatically appear on the details page of all published applications. Users who click the button will be redirected directly to the link and may voluntarily provide financial support to the developer.

#### 18.1.2 Donation Link Configuration Rules

**Configuration Entry:** Log in to the TNAS Developer Platform → Go to the "Personal information" page → Locate the "Donation Link" module → Click the "Edit" button on the right to modify.

**Format Requirements:**

- Type: String format; must be a valid HTTPS link (recommended);
- Length Limit: 10–255 characters;
- Optional: Developers may choose not to configure a donation link without affecting application publishing;
- Editable: Supports modification and deletion at any time; changes take effect immediately (the application details page updates synchronously).

**Display Logic:**

- The "Donate" button only appears on the application details page when the developer has configured a valid donation link; the button is hidden if not configured;
- The platform does not intervene in fund flow, settlement, or dispute resolution; it only provides a link redirect channel and does not charge any fees or commissions.

#### 18.1.3 Compliance Notes

- Donation links must comply with the laws and regulations of the applicable region and must not contain gambling, pornography, illegal finance, fraud, or other prohibited content;
- Tying donations to core application functionality (e.g., "basic features unavailable without donation") is prohibited; donations must remain voluntary;
- Developers bear full responsibility for link accessibility, compliance, and related tax and legal obligations.

### 18.2 Future Paid Application Feature (Planned)

#### 18.2.1 Feature Vision

To help developers earn reasonable development returns, the TNAS application ecosystem will introduce a paid application commercialization program in the future, providing a compliant and transparent paid distribution channel for quality applications. This will allow developers' innovation and investment to yield corresponding returns while offering users more high-quality, professional application choices.

#### 18.2.2 Core Program Framework (Planned Direction)

| Module | Planned Details |
|--------|-----------------|
| **Pricing Models** | Supports multiple commercialization models, including:<br>1. One-time purchase: Users pay a fixed fee for permanent use of the application;<br>2. Subscription: Pay monthly/annually for ongoing updates and technical support;<br>3. Premium feature unlock: Basic features free, advanced features require paid unlock. |
| **Pricing & Revenue Sharing** | 1. Developer sets their own pricing; the platform provides suggested pricing range references;<br>2. Transparent revenue sharing mechanism: Developers receive the vast majority of revenue; the platform charges a small technical service fee (specific ratios to be announced later);<br>3. Settlement cycle: Supports settlement by calendar month/quarter, with clear order and reconciliation data. |
| **Review & Publishing** | 1. Paid applications must pass additional quality and compliance review (including feature completeness, user agreement, privacy policy, etc.);<br>2. Clear feature descriptions, changelogs, and after-sales support commitments must be provided;<br>3. Free trial/limited-time experience support to lower the user decision threshold. |
| **Rights & Protections** | 1. Developer dashboard providing paid data panels (downloads, paid conversion rate, user reviews, etc.);<br>2. Platform provides user complaint handling and dispute mediation channels;<br>3. Featured placements, traffic boosts, and other support resources for quality paid applications. |

#### 18.2.3 Developer Preparation Recommendations

To prepare for the launch of paid application features, developers are advised to prepare in advance:

- **Polish Application Quality:** Focus on solving real user pain points, optimize feature stability, performance, and user experience to build differentiated competitiveness;
- **Improve Supporting Services:** Prepare clear user documentation, update plans, and technical support channels to increase users' willingness to pay;
- **Proactive Compliance Preparation:** Review application data processing logic, prepare compliance documents such as privacy policies and user agreements in preparation for paid publishing review;
- **Define Commercialization Path:** Based on application positioning, plan the pricing model (e.g., one-time purchase/subscription) and pricing strategy in advance to match the consumption habits of the target user group.

### 18.3 Additional Notes

- The "paid application feature" described in this chapter represents a future planned direction; the specific launch date and detailed rules will be subject to subsequent platform announcements;
- The platform will open a developer reservation channel before feature launch, prioritizing quality applications for testing and publishing support;
- If developers have suggestions or questions about the commercialization program, they may provide feedback through the Developer Platform ticket channel.

---

← [Previous: Operations & Delisting](17_Operations_Delisting.md) &nbsp;&nbsp;|&nbsp;&nbsp; [Next: FAQ](19_FAQ.md) → &nbsp;&nbsp;|&nbsp;&nbsp; [📖 Return to TOC](../README.md)
