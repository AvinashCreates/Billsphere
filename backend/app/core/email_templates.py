BRAND_NAME = "Billsphere"
PURPLE_DARK = "#2C1F7A"
PURPLE = "#4F46E5"
PURPLE_LIGHT = "#EEF2FF"
TEXT_COLOR = "#1F2937"
MUTED_COLOR = "#6B7280"
WHITE = "#FFFFFF"


def _header(title_line1: str, title_line2: str, subtitle: str, icon_svg: str) -> str:
    """Purple gradient banner with wave divider + illustration, matches the screenshot header."""
    return f"""
    <tr>
      <td style="padding:0; background-color:{PURPLE_DARK}; border-radius:16px 16px 0 0;">
        <table role="presentation" width="100%" style="border-collapse:collapse;">
          <tr>
            <td style="padding:28px 32px 8px;">
              <table role="presentation">
                <tr>
                  <td style="background-color:{PURPLE}; border-radius:10px; padding:8px 10px; text-align:center;">
                    <span style="color:#fff; font-size:16px;">&#128196;</span>
                  </td>
                  <td style="padding-left:10px; color:#fff; font-size:18px; font-weight:700;">
                    {BRAND_NAME}
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="padding:8px 32px 40px;">
              <table role="presentation" width="100%">
                <tr>
                  <td style="vertical-align:middle;">
                    <p style="margin:0; color:#fff; font-size:26px; font-weight:800; line-height:1.25;">
                      {title_line1}<br/>
                      <span style="color:#C7D2FE;">{title_line2}</span>
                    </p>
                    <p style="margin:10px 0 0; color:#C7D2FE; font-size:13px; line-height:1.5; max-width:260px;">
                      {subtitle}
                    </p>
                  </td>
                  <td style="width:110px; vertical-align:middle; text-align:right;">
                    {icon_svg}
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </td>
    </tr>
    <tr>
      <td style="line-height:0; background-color:{PURPLE_DARK};">
        <svg viewBox="0 0 600 40" width="100%" height="40" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M0,40 L0,20 Q150,45 300,20 T600,20 L600,40 Z" fill="{WHITE}"></path>
        </svg>
      </td>
    </tr>
    """


ENVELOPE_ICON = """
<svg width="90" height="90" viewBox="0 0 90 90" xmlns="http://www.w3.org/2000/svg">
  <rect x="10" y="30" width="70" height="48" rx="8" fill="#EEF2FF"/>
  <path d="M10 34 L45 60 L80 34" stroke="#818CF8" stroke-width="3" fill="none"/>
  <circle cx="63" cy="24" r="16" fill="#4F46E5"/>
  <path d="M56 24 L61 29 L71 18" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""

BELL_ICON = """
<svg width="90" height="90" viewBox="0 0 90 90" xmlns="http://www.w3.org/2000/svg">
  <circle cx="45" cy="42" r="26" fill="#EEF2FF"/>
  <path d="M45 24c-8 0-13 6-13 15v8l-5 7h36l-5-7v-8c0-9-5-15-13-15z" fill="#818CF8"/>
  <path d="M39 56a6 6 0 0 0 12 0" fill="#818CF8"/>
  <circle cx="66" cy="24" r="14" fill="#DC2626"/>
  <text x="66" y="29" font-size="14" fill="#fff" text-anchor="middle" font-family="Arial" font-weight="bold">!</text>
</svg>
"""

USER_CHECK_ICON = """
<svg width="90" height="90" viewBox="0 0 90 90" xmlns="http://www.w3.org/2000/svg">
  <circle cx="40" cy="35" r="14" fill="#818CF8"/>
  <path d="M18 68c0-14 10-22 22-22s22 8 22 22" fill="#818CF8"/>
  <circle cx="63" cy="24" r="16" fill="#4F46E5"/>
  <path d="M56 24 L61 29 L71 18" stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""


def _stat_cell(label: str, value: str, value_color: str, icon_char: str) -> str:
    return f"""
    <td style="text-align:center; padding:16px 8px; width:33%;">
      <div style="width:34px; height:34px; background-color:{PURPLE_LIGHT}; border-radius:50%; margin:0 auto 8px; line-height:34px; font-size:14px;">
        {icon_char}
      </div>
      <p style="margin:0; color:{MUTED_COLOR}; font-size:10px; text-transform:uppercase; letter-spacing:0.5px;">{label}</p>
      <p style="margin:4px 0 0; color:{value_color}; font-size:14px; font-weight:700;">{value}</p>
    </td>
    """


def _stat_row(cells: list[str]) -> str:
    tds = "".join(cells)
    return f"""
    <table role="presentation" width="100%" style="background-color:{PURPLE_LIGHT}; border-radius:12px; margin:24px 0; border-collapse:collapse;">
      <tr>{tds}</tr>
    </table>
    """


def _button(label: str, href: str = "#") -> str:
    return f"""
    <table role="presentation" style="margin:8px 0 24px;">
      <tr>
        <td style="background-color:{PURPLE}; border-radius:10px;">
          <a href="{href}" style="display:inline-block; padding:13px 30px; color:#ffffff; font-size:14px; font-weight:700; text-decoration:none;">
            {label} &nbsp;&rarr;
          </a>
        </td>
      </tr>
    </table>
    """


def _feature_row(items: list[tuple[str, str, str]]) -> str:
    """items: list of (icon_char, title, description)"""
    cells = "".join(f"""
    <td style="vertical-align:top; padding:14px 10px; width:33%;">
      <div style="width:28px; height:28px; background-color:{PURPLE_LIGHT}; border-radius:50%; text-align:center; line-height:28px; font-size:13px; margin-bottom:6px;">
        {icon}
      </div>
      <p style="margin:0; color:{TEXT_COLOR}; font-size:12px; font-weight:700;">{title}</p>
      <p style="margin:2px 0 0; color:{MUTED_COLOR}; font-size:11px; line-height:1.4;">{desc}</p>
    </td>
    """ for icon, title, desc in items)
    return f"""
    <table role="presentation" width="100%" style="background-color:{PURPLE_LIGHT}; border-radius:12px; margin:8px 0 24px; border-collapse:collapse;">
      <tr>{cells}</tr>
    </table>
    """


def _footer() -> str:
    social_circle = lambda label: f"""
    <td style="padding:0 6px;">
      <div style="width:28px; height:28px; background-color:{PURPLE_DARK}; border-radius:50%; text-align:center; line-height:28px; color:#fff; font-size:11px; font-family:Arial;">
        {label}
      </div>
    </td>
    """
    return f"""
    <tr>
      <td style="text-align:center; padding:20px 8px 4px;">
        <p style="margin:0; color:{PURPLE}; font-size:13px; font-weight:700;">&#9829; Thank you for choosing {BRAND_NAME}!</p>
        <p style="margin:6px 0 16px; color:{MUTED_COLOR}; font-size:12px;">If you have any questions, just reply to this email.</p>
        <table role="presentation" style="margin:0 auto 12px;">
          <tr>
            {social_circle("f")}
            {social_circle("t")}
            {social_circle("in")}
          </tr>
        </table>
        <p style="margin:0; color:#9CA3AF; font-size:11px;">© 2026 {BRAND_NAME}. All rights reserved.</p>
      </td>
    </tr>
    """


def _wrapper(header_html: str, body_inner: str) -> str:
    return f"""
    <div style="background-color:#F4F4F7; padding:24px 16px; font-family:-apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;">
      <table role="presentation" width="100%" style="max-width:560px; margin:0 auto; border-collapse:collapse; background-color:#ffffff; border-radius:16px; overflow:hidden; box-shadow:0 2px 8px rgba(0,0,0,0.06);">
        {header_html}
        <tr>
          <td style="padding:8px 32px 8px;">
            {body_inner}
          </td>
        </tr>
        {_footer()}
      </table>
    </div>
    """


# ---------------------------------------------------------------------
# WELCOME
# ---------------------------------------------------------------------
def welcome_email(user_name: str) -> tuple[str, str]:
    subject = f"Welcome to {BRAND_NAME}!"
    header = _header(
        "Welcome to",
        f"{BRAND_NAME}! &#128075;",
        "Your account is ready. Let's get your billing sorted, one plan at a time.",
        USER_CHECK_ICON,
    )
    body = f"""
      <div style="text-align:center; margin:8px 0 4px;">
        <div style="width:44px; height:44px; background-color:{PURPLE_LIGHT}; border-radius:50%; margin:0 auto 12px; line-height:44px; font-size:20px;">&#127881;</div>
        <p style="margin:0; color:{TEXT_COLOR}; font-size:18px; font-weight:800;">
          Hi <span style="color:{PURPLE};">{user_name}</span>,
        </p>
        <p style="margin:8px 0 0; color:{MUTED_COLOR}; font-size:13px;">
          Thanks for joining {BRAND_NAME}. Browse plans and manage billing anytime from your dashboard.
        </p>
      </div>
      <div style="text-align:center;">
        {_button("Go to Dashboard")}
      </div>
      {_feature_row([
          ("&#128274;", "Secure Payments", "Your transactions are 100% secure."),
          ("&#127911;", "24/7 Support", "We're here whenever you need us."),
          ("&#9993;", "Smart Reminders", "Never miss a payment with timely alerts."),
      ])}
    """
    return subject, _wrapper(header, body)


# ---------------------------------------------------------------------
# SUBSCRIPTION CONFIRMATION
# ---------------------------------------------------------------------
def subscription_confirmation_email(customer_name: str, plan_name: str, billing_interval: str, deadline_str: str) -> tuple[str, str]:
    subject = f"You're all set — {plan_name} plan activated!"
    header = _header(
        "Subscription",
        "Activated! &#127881;",
        "Great choice! Your service is now active and all set to go.",
        ENVELOPE_ICON,
    )
    body = f"""
      <div style="text-align:center; margin:8px 0 4px;">
        <div style="width:44px; height:44px; background-color:{PURPLE_LIGHT}; border-radius:50%; margin:0 auto 12px; line-height:44px; font-size:20px;">&#127881;</div>
        <p style="margin:0; color:{TEXT_COLOR}; font-size:18px; font-weight:800;">
          Hi <span style="color:{PURPLE};">{customer_name}</span>,
        </p>
        <p style="margin:8px 0 0; color:{MUTED_COLOR}; font-size:13px;">
          Thank you for subscribing to {BRAND_NAME}. Here are your subscription details.
        </p>
      </div>
      {_stat_row([
          _stat_cell("Plan", plan_name, PURPLE, "&#128278;"),
          _stat_cell("Next Billing Date", deadline_str, PURPLE, "&#128197;"),
          _stat_cell("Billing Cycle", billing_interval.capitalize(), TEXT_COLOR, "&#128260;"),
      ])}
      <div style="text-align:center;">
        {_button("Manage Subscription")}
      </div>
      {_feature_row([
          ("&#128274;", "Secure Payments", "Your transactions are 100% secure."),
          ("&#127911;", "24/7 Support", "We're here whenever you need us."),
          ("&#9993;", "Smart Reminders", "Never miss a payment with timely alerts."),
      ])}
    """
    return subject, _wrapper(header, body)


# ---------------------------------------------------------------------
# DEADLINE REMINDER
# ---------------------------------------------------------------------
def deadline_reminder_email(customer_name: str, plan_name: str, deadline_str: str, days_left: int) -> tuple[str, str]:
    subject = f"Reminder: your {plan_name} plan renews in {days_left} day{'s' if days_left != 1 else ''}"
    header = _header(
        "Renewal",
        "Coming Up &#9200;",
        f"Your {plan_name} plan renews soon — a quick heads up so you're never caught off guard.",
        BELL_ICON,
    )
    urgency_color = "#DC2626" if days_left <= 1 else "#D97706"
    body = f"""
      <div style="text-align:center; margin:8px 0 4px;">
        <p style="margin:0; color:{TEXT_COLOR}; font-size:18px; font-weight:800;">
          Hi <span style="color:{PURPLE};">{customer_name}</span>,
        </p>
        <p style="margin:8px 0 0; color:{MUTED_COLOR}; font-size:13px;">
          This is a friendly reminder about your upcoming renewal.
        </p>
      </div>
      {_stat_row([
          _stat_cell("Plan", plan_name, PURPLE, "&#128278;"),
          _stat_cell("Renews On", deadline_str, urgency_color, "&#128197;"),
          _stat_cell("Days Left", str(days_left), urgency_color, "&#9200;"),
      ])}
      <div style="text-align:center;">
        {_button("Review Billing")}
      </div>
      {_feature_row([
          ("&#128274;", "Secure Payments", "Your transactions are 100% secure."),
          ("&#127911;", "24/7 Support", "We're here whenever you need us."),
          ("&#9993;", "Smart Reminders", "Never miss a payment with timely alerts."),
      ])}
    """
    return subject, _wrapper(header, body)


def customer_invite_email(customer_name: str, set_password_link: str) -> tuple[str, str]:
    subject = f"You've been added to {BRAND_NAME} — set your password"
    header = _header(
        "You're",
        "All Set! &#128273;",
        "An account has been created for you. Set a password to log in.",
        USER_CHECK_ICON,
    )
    body = f"""
      <div style="text-align:center; margin:8px 0 4px;">
        <p style="margin:0; color:{TEXT_COLOR}; font-size:18px; font-weight:800;">
          Hi <span style="color:{PURPLE};">{customer_name}</span>,
        </p>
        <p style="margin:8px 0 0; color:{MUTED_COLOR}; font-size:13px;">
          An account has been created for you on {BRAND_NAME}. Click below to set your password and get started.
        </p>
      </div>
      <div style="text-align:center;">
        {_button("Set Your Password", set_password_link)}
      </div>
      <p style="color:{MUTED_COLOR}; font-size:12px; line-height:1.6; margin:12px 0 0; text-align:center;">
        This link expires in 48 hours. If you didn't request this, you can ignore this email.
      </p>
    """
    return subject, _wrapper(header, body)
def trial_activated_email(customer_name: str, plan_name: str, trial_days: int, trial_end_str: str) -> tuple[str, str]:
    subject = f"Your {trial_days}-day trial of {plan_name} has started!"
    header = _header(
        "Trial",
        "Activated! &#9203;",
        f"Enjoy full access to {plan_name} for {trial_days} days, on us.",
        BELL_ICON,
    )
    body = f"""
      <div style="text-align:center; margin:8px 0 4px;">
        <p style="margin:0; color:{TEXT_COLOR}; font-size:18px; font-weight:800;">
          Hi <span style="color:{PURPLE};">{customer_name}</span>,
        </p>
        <p style="margin:8px 0 0; color:{MUTED_COLOR}; font-size:13px;">
          Your free trial of <strong style="color:{TEXT_COLOR};">{plan_name}</strong> is now active.
        </p>
      </div>
      {_stat_row([
          _stat_cell("Plan", plan_name, PURPLE, "&#128278;"),
          _stat_cell("Trial Length", f"{trial_days} days", PURPLE, "&#9203;"),
          _stat_cell("Trial Ends", trial_end_str, TEXT_COLOR, "&#128197;"),
      ])}
      <div style="text-align:center;">
        {_button("Manage Trial")}
      </div>
      <p style="color:{MUTED_COLOR}; font-size:12px; line-height:1.6; margin:12px 0 0; text-align:center;">
        You can continue to a paid plan anytime from your dashboard, before or after the trial ends.
      </p>
    """
    return subject, _wrapper(header, body)


def past_due_email(customer_name: str, plan_name: str, due_date_str: str) -> tuple[str, str]:
    subject = f"Action needed — your {plan_name} plan is past due"
    header = _header(
        "Payment",
        "Past Due &#9888;",
        f"Your {plan_name} plan needs your attention to keep running.",
        BELL_ICON,
    )
    body = f"""
      <div style="text-align:center; margin:8px 0 4px;">
        <p style="margin:0; color:{TEXT_COLOR}; font-size:18px; font-weight:800;">
          Hi <span style="color:{PURPLE};">{customer_name}</span>,
        </p>
        <p style="margin:8px 0 0; color:{MUTED_COLOR}; font-size:13px;">
          Your <strong style="color:{TEXT_COLOR};">{plan_name}</strong> plan was due on {due_date_str} and hasn't been renewed yet.
        </p>
      </div>
      <table role="presentation" width="100%" style="background-color:#FEF2F2; border-left:4px solid #DC2626; border-radius:6px; margin:0 0 20px;">
        <tr>
          <td style="padding:16px 20px;">
            <p style="margin:0; color:#DC2626; font-size:15px; font-weight:700;">
              Renew now to avoid losing access
            </p>
          </td>
        </tr>
      </table>
      <div style="text-align:center;">
        {_button("Renew Now")}
      </div>
    """
    return subject, _wrapper(header, body)


def cancellation_email(customer_name: str, plan_name: str, immediate: bool, effective_date_str: str) -> tuple[str, str]:
    subject = f"Your {plan_name} plan has been cancelled" if immediate else f"Your {plan_name} plan is set to cancel"
    header = _header(
        "Subscription",
        "Cancelled" if immediate else "Cancelling Soon",
        f"We're sorry to see you go from {plan_name}.",
        USER_CHECK_ICON,
    )
    timing_text = (
        f"Your access ended immediately, effective {effective_date_str}."
        if immediate
        else f"Your plan stays active until {effective_date_str}, then it will cancel."
    )
    body = f"""
      <div style="text-align:center; margin:8px 0 4px;">
        <p style="margin:0; color:{TEXT_COLOR}; font-size:18px; font-weight:800;">
          Hi <span style="color:{PURPLE};">{customer_name}</span>,
        </p>
        <p style="margin:8px 0 0; color:{MUTED_COLOR}; font-size:13px;">
          {timing_text}
        </p>
      </div>
      <div style="text-align:center;">
        {_button("Browse Plans")}
      </div>
      <p style="color:{MUTED_COLOR}; font-size:12px; line-height:1.6; margin:12px 0 0; text-align:center;">
        Changed your mind? You can resubscribe anytime from your dashboard.
      </p>
    """
    return subject, _wrapper(header, body)


def reactivation_email(customer_name: str, plan_name: str, new_period_end_str: str) -> tuple[str, str]:
    subject = f"Your {plan_name} plan is active again!"
    header = _header(
        "Plan",
        "Reactivated! &#9989;",
        f"Good news — {plan_name} is up and running again.",
        ENVELOPE_ICON,
    )
    body = f"""
      <div style="text-align:center; margin:8px 0 4px;">
        <p style="margin:0; color:{TEXT_COLOR}; font-size:18px; font-weight:800;">
          Hi <span style="color:{PURPLE};">{customer_name}</span>,
        </p>
        <p style="margin:8px 0 0; color:{MUTED_COLOR}; font-size:13px;">
          Your <strong style="color:{TEXT_COLOR};">{plan_name}</strong> plan is now active again.
        </p>
      </div>
      {_stat_row([
          _stat_cell("Plan", plan_name, PURPLE, "&#128278;"),
          _stat_cell("Active Until", new_period_end_str, PURPLE, "&#128197;"),
          _stat_cell("Status", "Active", "#059669", "&#9989;"),
      ])}
      <div style="text-align:center;">
        {_button("View Dashboard")}
      </div>
    """
    return subject, _wrapper(header, body)