/**
 * app.js — Zudio Store Operations Dashboard & Copilot Frontend Logic
 * Supports Multi-Tab Views, High-Fidelity Chart.js Visuals, and Gemini 3.5 Copilot
 */

// Chart instances store
const charts = {
  topProducts: null,
  weekday: null,
  size: null,
  category: null,
  demographics: null,
  payment: null,
  overviewMini: null,
  overviewDonut: null
};

// Cached metrics
let cachedMetrics = null;

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  setupTabs();
  setupDrawerControls();
  setupChatHandlers();
  initDashboard();
});

/**
 * 1. Tab Switching System
 */
function setupTabs() {
  const tabButtons = document.querySelectorAll(".nav-tab");
  const tabPanes = document.querySelectorAll(".tab-pane");

  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-tab");

      // Update button active state
      tabButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      // Update pane active state
      tabPanes.forEach(pane => {
        pane.classList.remove("active");
        if (pane.id === targetId) {
          pane.classList.add("active");
        }
      });

      // Trigger chart resize on tab reveal
      window.dispatchEvent(new Event("resize"));
    });
  });

  const printBtn = document.getElementById("printReportBtn");
  if (printBtn) {
    printBtn.addEventListener("click", () => {
      window.print();
    });
  }
}

/**
 * 2. Copilot Full-Screen Modal Controls
 */
function setupDrawerControls() {
  const toggleBtn  = document.getElementById("toggleChatBtn");
  const closeBtn   = document.getElementById("closeDrawerBtn");
  const clearBtn   = document.getElementById("clearChatBtn");
  const overlay    = document.getElementById("copilotOverlay");
  const toggleText = document.getElementById("chatToggleText");

  function openCopilot() {
    overlay.classList.add("open");
    document.body.style.overflow = "hidden"; // prevent background scroll
    if (toggleText) toggleText.textContent = "AI Copilot";
    // Focus the chat input after animation
    setTimeout(() => {
      const input = document.getElementById("chatInput");
      if (input) input.focus();
    }, 380);
  }

  function closeCopilot() {
    overlay.classList.remove("open");
    document.body.style.overflow = "";
    if (toggleText) toggleText.textContent = "AI Copilot";
  }

  if (toggleBtn) toggleBtn.addEventListener("click", openCopilot);
  if (closeBtn)  closeBtn.addEventListener("click", closeCopilot);

  // Click on the dark backdrop (outside the panel) to close
  if (overlay) {
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) closeCopilot();
    });
  }

  // Escape key closes
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && overlay.classList.contains("open")) {
      closeCopilot();
    }
  });

  // Clear chat button
  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      const container = document.getElementById("chatMessages");
      if (!container) return;
      // Keep the welcome message (first child), remove the rest
      while (container.children.length > 1) {
        container.removeChild(container.lastChild);
      }
    });
  }
}

/**
 * 3. Ingests Deterministic Metrics and Renders UI + Visual Charts
 */
async function initDashboard() {
  try {
    const res = await fetch("/api/metrics");
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    cachedMetrics = data;

    populateKPIs(data);
    renderAllCharts(data);
  } catch (err) {
    console.warn("Could not fetch /api/metrics, applying precomputed fallback metrics:", err);
    loadStaticFallback();
  }
}

/**
 * Populates top KPI metric cards and target progress
 */
function populateKPIs(data) {
  const ov = data.overview;
  const demo = data.demographic_patterns;

  const kpiRev = document.getElementById("kpiRevenue");
  if (kpiRev) kpiRev.textContent = `₹${ov.total_revenue.toLocaleString("en-IN")}`;

  const kpiUnits = document.getElementById("kpiUnits");
  if (kpiUnits) kpiUnits.innerHTML = `${ov.total_units_sold} <span class="unit-tag">Items</span>`;

  const kpiATV = document.getElementById("kpiATV");
  if (kpiATV) kpiATV.textContent = `₹${ov.average_transaction_value.toFixed(2)}`;

  const kpiDemo = document.getElementById("kpiDemographics");
  if (kpiDemo) kpiDemo.innerHTML = `${demo.young_adult_rev_share}% <span class="unit-tag">Young Adults</span>`;
}

/**
 * Renders all Chart.js visualizations across tabs
 */
function renderAllCharts(data) {
  // 1. Top 10 Best Sellers
  renderTopProductsChart(data.product_performance.top_10);

  // 2. Weekday Trajectory
  renderWeekdayChart(data.weekday_analysis.breakdown);

  // 3. Garment Size Demand Donut
  renderSizeChart(data.size_analysis.distribution);

  // 4. Category Revenue vs Discount
  renderCategoryChart(data.discount_efficiency.categories);

  // 5. Demographics Age Groups
  renderDemographicsChart(data.demographic_patterns.age_groups);

  // 6. Payment Channels
  renderPaymentChart(data.demographic_patterns.payment_methods);

  // Overview Tab Mini Previews
  renderOverviewMiniChart(data.product_performance.top_3);
  renderOverviewDonutChart(data.size_analysis.distribution);
}

/**
 * Chart 1: Top 10 Products by Sales Volume & Revenue
 */
function renderTopProductsChart(products) {
  const canvas = document.getElementById("topProductsChart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  const labels = products.map(p => p.product_name);
  const units = products.map(p => p.units_sold);
  const revenues = products.map(p => p.revenue);

  if (charts.topProducts) charts.topProducts.destroy();

  charts.topProducts = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Units Sold",
          data: units,
          backgroundColor: "#6366f1",
          borderRadius: 4,
          barPercentage: 0.6,
          yAxisID: "y"
        },
        {
          label: "Revenue (₹)",
          data: revenues,
          backgroundColor: "#06b6d4",
          borderRadius: 4,
          barPercentage: 0.6,
          yAxisID: "y1"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: context => context.dataset.label === "Revenue (₹)"
              ? `Revenue: ₹${context.raw.toLocaleString("en-IN")}`
              : `Units Sold: ${context.raw} pcs`
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: "#94a3b8", font: { size: 10 } }
        },
        y: {
          type: "linear",
          position: "left",
          title: { display: true, text: "Units Sold", color: "#6366f1", font: { size: 11, weight: "bold" } },
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          ticks: { color: "#94a3b8" }
        },
        y1: {
          type: "linear",
          position: "right",
          title: { display: true, text: "Revenue (₹)", color: "#06b6d4", font: { size: 11, weight: "bold" } },
          grid: { drawOnChartArea: false },
          ticks: {
            color: "#94a3b8",
            callback: v => "₹" + (v >= 1000 ? (v / 1000).toFixed(0) + "k" : v)
          }
        }
      }
    }
  });
}

/**
 * Chart 2: Weekday Revenue Breakdown
 */
function renderWeekdayChart(breakdown) {
  const canvas = document.getElementById("weekdayChart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  const labels = breakdown.map(d => d.day_of_week.substring(0, 3));
  const revenues = breakdown.map(d => d.revenue);

  // Tuesday alert color
  const bgColors = breakdown.map(d => d.day_of_week === "Tuesday" ? "#f59e0b" : "#4f46e5");

  if (charts.weekday) charts.weekday.destroy();

  charts.weekday = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Revenue (₹)",
        data: revenues,
        backgroundColor: bgColors,
        borderRadius: 6,
        barPercentage: 0.55
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: context => `Revenue: ₹${context.raw.toLocaleString("en-IN")}`
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: "#94a3b8", font: { size: 11, weight: "bold" } }
        },
        y: {
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          ticks: {
            color: "#94a3b8",
            callback: v => "₹" + (v / 1000).toFixed(0) + "k"
          }
        }
      }
    }
  });
}

/**
 * Chart 3: Size Demand Distribution (Donut Chart)
 */
function renderSizeChart(distribution) {
  const canvas = document.getElementById("sizeChart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  const labels = distribution.map(s => `Size ${s.size}`);
  const shares = distribution.map(s => s.share_pct);

  const colors = ["#6366f1", "#06b6d4", "#10b981", "#8b5cf6", "#f43f5e"];

  if (charts.size) charts.size.destroy();

  charts.size = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: shares,
        backgroundColor: colors,
        borderWidth: 2,
        borderColor: "#111827"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "66%",
      plugins: {
        legend: {
          position: "right",
          labels: { color: "#94a3b8", font: { size: 11 }, boxWidth: 12 }
        },
        tooltip: {
          callbacks: {
            label: context => `${context.label}: ${context.raw}% of demand`
          }
        }
      }
    }
  });
}

/**
 * Chart 4: Category Revenue vs Discount
 */
function renderCategoryChart(categories) {
  const canvas = document.getElementById("categoryChart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  const labels = categories.map(c => c.category);
  const revShares = categories.map(c => c.revenue_share_pct);
  const discounts = categories.map(c => c.avg_discount);

  if (charts.category) charts.category.destroy();

  charts.category = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Revenue Contribution (%)",
          data: revShares,
          backgroundColor: "#3b82f6",
          borderRadius: 4
        },
        {
          label: "Average Discount (%)",
          data: discounts,
          backgroundColor: "#a855f7",
          borderRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: "#94a3b8", font: { size: 11 } }
        },
        tooltip: {
          callbacks: {
            label: context => `${context.dataset.label}: ${context.raw}%`
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: "#94a3b8", font: { size: 11 } }
        },
        y: {
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          ticks: {
            color: "#94a3b8",
            callback: v => v + "%"
          }
        }
      }
    }
  });
}

/**
 * Chart 5: Demographics Age Group Distribution
 */
function renderDemographicsChart(ageGroups) {
  const canvas = document.getElementById("demographicsChart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  const labels = ageGroups.map(a => a.age_group);
  const revShares = ageGroups.map(a => a.rev_share);

  if (charts.demographics) charts.demographics.destroy();

  charts.demographics = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Revenue Share (%)",
        data: revShares,
        backgroundColor: ["#6366f1", "#06b6d4", "#f59e0b", "#10b981"],
        borderRadius: 6,
        barPercentage: 0.55
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: context => `Share: ${context.raw}% of monthly revenue`
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: "#94a3b8", font: { size: 10 } }
        },
        y: {
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          ticks: {
            color: "#94a3b8",
            callback: v => v + "%"
          }
        }
      }
    }
  });
}

/**
 * Chart 6: Payment Methods Breakdown
 */
function renderPaymentChart(paymentMethods) {
  const canvas = document.getElementById("paymentChart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  const labels = paymentMethods.map(p => p.payment_method);
  const shares = paymentMethods.map(p => p.share_pct);

  if (charts.payment) charts.payment.destroy();

  charts.payment = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: shares,
        backgroundColor: ["#10b981", "#6366f1", "#f59e0b"],
        borderWidth: 2,
        borderColor: "#111827"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "68%",
      plugins: {
        legend: {
          position: "right",
          labels: { color: "#94a3b8", font: { size: 11 }, boxWidth: 12 }
        },
        tooltip: {
          callbacks: {
            label: context => `${context.label}: ${context.raw}% of transactions`
          }
        }
      }
    }
  });
}

/**
 * Overview Tab Mini Chart: Top 3 Preview
 */
function renderOverviewMiniChart(top3) {
  const canvas = document.getElementById("overviewMiniChart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  const labels = top3.map(p => p.product_name);
  const units = top3.map(p => p.units_sold);

  if (charts.overviewMini) charts.overviewMini.destroy();

  charts.overviewMini = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        label: "Units Sold",
        data: units,
        backgroundColor: "#6366f1",
        borderRadius: 4,
        barPercentage: 0.5
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: "#94a3b8", font: { size: 10 } }
        },
        y: {
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          ticks: { color: "#94a3b8" }
        }
      }
    }
  });
}

/**
 * Overview Tab Donut Chart: Size Preview
 */
function renderOverviewDonutChart(distribution) {
  const canvas = document.getElementById("overviewDonutChart");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  const labels = distribution.map(s => `Size ${s.size}`);
  const shares = distribution.map(s => s.share_pct);

  if (charts.overviewDonut) charts.overviewDonut.destroy();

  charts.overviewDonut = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: shares,
        backgroundColor: ["#6366f1", "#06b6d4", "#10b981", "#8b5cf6", "#f43f5e"],
        borderWidth: 2,
        borderColor: "#111827"
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "65%",
      plugins: {
        legend: {
          position: "right",
          labels: { color: "#94a3b8", font: { size: 10 }, boxWidth: 10 }
        }
      }
    }
  });
}

/**
 * 4. Chat Form Handlers & Copilot Interaction
 */
function setupChatHandlers() {
  const form = document.getElementById("chatForm");
  const input = document.getElementById("chatInput");
  const clearBtn = document.getElementById("clearChatBtn");
  const refreshBtn = document.getElementById("refreshBtn");

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const query = input.value.trim();
      if (!query) return;

      appendUserMessage(query);
      input.value = "";
      await sendQueryToCopilot(query);
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      const container = document.getElementById("chatMessages");
      container.innerHTML = `
        <div class="chat-message assistant-msg">
          <div class="msg-avatar">AI</div>
          <div class="msg-bubble">
            <p>Chat cleared! Ask me any retail operations question in <strong>English or Hindi</strong>.</p>
          </div>
        </div>
      `;
    });
  }

  if (refreshBtn) {
    refreshBtn.addEventListener("click", () => {
      initDashboard();
      refreshBtn.classList.add("spinning");
      setTimeout(() => refreshBtn.classList.remove("spinning"), 600);
    });
  }

  const chipsScroll = document.getElementById("chipsScroll");
  if (chipsScroll) {
    // Horizontal wheel scroll
    chipsScroll.addEventListener("wheel", (e) => {
      if (e.deltaY !== 0) {
        e.preventDefault();
        chipsScroll.scrollLeft += e.deltaY * 1.5;
      }
    }, { passive: false });

    // Drag to scroll
    let isDown = false;
    let startX = 0;
    let scrollLeft = 0;

    chipsScroll.addEventListener("mousedown", (e) => {
      isDown = true;
      startX = e.pageX - chipsScroll.offsetLeft;
      scrollLeft = chipsScroll.scrollLeft;
      chipsScroll.style.cursor = "grabbing";
    });
    chipsScroll.addEventListener("mouseleave", () => {
      isDown = false;
      chipsScroll.style.cursor = "grab";
    });
    chipsScroll.addEventListener("mouseup", () => {
      isDown = false;
      chipsScroll.style.cursor = "grab";
    });
    chipsScroll.addEventListener("mousemove", (e) => {
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - chipsScroll.offsetLeft;
      const walk = (x - startX) * 1.6;
      chipsScroll.scrollLeft = scrollLeft - walk;
    });
  }
}

/**
 * Predefined Copilot Prompts in clean English (except Hindi floor briefing)
 */
window.COPILOT_PROMPTS = {
  // Priority 1: The 5 Core Assessment Questions
  q1_products: "Which products are selling well and which are not? Find the top 3 best-selling products and the 3 worst-selling products. For each slow product, give one possible reason in simple words — is it too expensive? Wrong size range? Low discount?",
  q2_sizes: "Which size keeps running out? Which size is barely moving? Look at how much of each size was sold. Tell the store manager which sizes to order more of next month, and which sizes they may have ordered too much of.",
  q3_weekday: "Which day of the week is the busiest? Which is the slowest? Tell the manager on which day the store makes the most money. And on the slowest day — should the store run a special offer to bring more customers in?",
  q4_customers: "Who is buying what? Find at least 2 interesting customer buying patterns. Spot something non-obvious from the September sales data.",
  q5_actions: "Give the store manager 3 clear actions for next week. These must be specific and actionable, complete with verified data evidence, business rationale, and expected financial impact.",

  // Priority 2: Detailed Executive & Floor Reports
  english_brief: "Provide a comprehensive executive operational briefing in English summarizing our September store performance, key wins, inventory stockout risks, and immediate directives for the store manager.",
  hindi_brief: "Can you give me a summary in Hindi for my floor supervisors? (सितंबर स्टोर प्रदर्शन सारांश - टीम के लिए जरूरी निर्देश)",

  // Priority 3: Operational Extensions & Traps
  q6_basket: "Based on our September bill-level transaction data where multi-item bills share the same bill_id:\n1. What is the average basket size (UPT - Units Per Transaction) and Average Order Value (AOV)?\n2. What are the most common co-purchased product pairs bought together in multi-item bills (e.g., Kurti + Scarf, Jeans + Belt)?\n3. Which merchandise category functions as an impulse add-on, and what floor placement strategy should we implement at checkout?",
  q7_weekend: "For the upcoming weekend (Saturday-Sunday), based on our September sales velocity and inventory patterns:\n1. Which specific product should we put on a clearance sale this weekend?\n2. What is the business reasoning (e.g., slow-moving velocity, post-festival demand cliff, high price resistance)?\n3. What exact discount percentage do you recommend, and how should it be merchandised on the floor?",
  q8_wow: "Analyze our September performance week-on-week across the 4 weekly periods (Week 1: Sept 1-7, Week 2: Sept 8-14, Week 3: Sept 15-21, Week 4: Sept 22-30):\n1. Which week generated the highest revenue, and which was the lowest?\n2. Does the data confirm an urban salary-cycle pattern (strong month start vs sharp month-end slump)?\n3. What proactive strategy and promotional countermeasures should the store manager deploy to combat month-end slowdowns?",
  avoid: "What counterproductive retail practices did you detect that our store should immediately stop doing (specifically regarding the 50% accessory discount trap)?",

  // Aliases & Backward Compatibility
  stockout: "Analyze our garment size inventory: Which specific product and size suffered a stockout crisis, what was the estimated revenue loss, and what is our emergency replenishment directive?",
  tuesday: "Why was Tuesday our slowest day of the week, what happened during the Tuesday September 16 anomaly, and what specific mid-week bundle promotion should we run?",
  actions: "Provide 3 high-priority operational actions for the store manager next week, complete with data evidence, financial impact, and execution steps.",
  segment: "Who is our core customer demographic segment, what merchandise do they buy, and how do we maximize customer retention and basket value?",
  margin: "Which products have the worst sales velocity and margin efficiency, and what markdown or delisting strategy should we execute?"
};

/**
 * Click handler to smoothly scroll the quick chips container
 */
window.scrollChips = function(offset) {
  const container = document.getElementById("chipsScroll");
  if (container) {
    container.scrollBy({ left: offset, behavior: "smooth" });
  }
};

/**
 * Click handler for Quick Chips — opens copilot modal and fires question
 */
window.askCopilot = function(questionOrKey) {
  const prompt = (window.COPILOT_PROMPTS && window.COPILOT_PROMPTS[questionOrKey]) ? window.COPILOT_PROMPTS[questionOrKey] : questionOrKey;
  // Open fullscreen overlay if not already open
  const overlay = document.getElementById("copilotOverlay");
  if (overlay && !overlay.classList.contains("open")) {
    overlay.classList.add("open");
    document.body.style.overflow = "hidden";
  }
  appendUserMessage(prompt);
  sendQueryToCopilot(prompt);
};

/**
 * Appends User message bubble
 */
function appendUserMessage(text) {
  const container = document.getElementById("chatMessages");
  const msgEl = document.createElement("div");
  msgEl.className = "chat-message user-msg";
  msgEl.innerHTML = `
    <div class="msg-avatar">You</div>
    <div class="msg-bubble">${escapeHtml(text)}</div>
  `;
  container.appendChild(msgEl);
  container.scrollTop = container.scrollHeight;
}

/**
 * Sends question to /api/chat endpoint and renders assistant reply
 */
async function sendQueryToCopilot(prompt) {
  const typing = document.getElementById("typingIndicator");
  const container = document.getElementById("chatMessages");

  if (typing) typing.style.display = "flex";
  container.scrollTop = container.scrollHeight;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: prompt })
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    
    if (typing) typing.style.display = "none";
    appendAssistantMessage(data.reply);

  } catch (err) {
    if (typing) typing.style.display = "none";
    console.error("Chat request failed:", err);
    appendAssistantMessage("I encountered an issue connecting to the AI service. Please verify your network connection or API quota.");
  }
}

/**
 * Appends Assistant response with clean HTML formatting and Copy Button
 */
function appendAssistantMessage(rawText) {
  const container = document.getElementById("chatMessages");
  const msgEl = document.createElement("div");
  msgEl.className = "chat-message assistant-msg";

  const formattedHtml = parseMarkdownToHtml(rawText);

  msgEl.innerHTML = `
    <div class="msg-avatar">AI</div>
    <div class="msg-bubble">
      ${formattedHtml}
      <div class="msg-action-bar">
        <button class="copy-btn" onclick="copyMessageText(this)">📋 Copy Briefing</button>
      </div>
    </div>
  `;
  container.appendChild(msgEl);
  container.scrollTop = container.scrollHeight;
}

/**
 * One-click copy message text for WhatsApp floor huddle sharing
 */
window.copyMessageText = function(btn) {
  const bubble = btn.closest(".msg-bubble");
  if (!bubble) return;

  // Clone bubble and remove action bar before copying text
  const clone = bubble.cloneNode(true);
  const actionEl = clone.querySelector(".msg-action-bar");
  if (actionEl) actionEl.remove();

  const plainText = clone.innerText.trim();
  navigator.clipboard.writeText(plainText).then(() => {
    const origText = btn.textContent;
    btn.textContent = "✓ Copied!";
    btn.classList.add("copied");
    setTimeout(() => {
      btn.textContent = origText;
      btn.classList.remove("copied");
    }, 2000);
  }).catch(err => {
    console.error("Clipboard copy failed:", err);
  });
};

/**
 * Robust Markdown-to-HTML parser for bullet points, bolding, numbered lists, and headers
 */
function parseMarkdownToHtml(md) {
  if (!md) return '';

  // Step 1: First sanitize any unmatched ** that would break rendering
  // Count occurrences - if odd number of **, add a closing one at end
  const boldCount = (md.match(/\*\*/g) || []).length;
  if (boldCount % 2 !== 0) {
    md = md + '**';
  }

  let html = md
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    // Horizontal rules
    .replace(/^---$/gim, "<hr style='border:0;border-top:1px solid rgba(255,255,255,0.1);margin:0.75rem 0;'>")
    // Headers (process before bold to avoid conflicts)
    .replace(/^#### (.*$)/gim, "<strong style='display:block;margin-top:0.5rem;color:#fde68a;font-size:0.875rem;'>$1</strong>")
    .replace(/^### (.*$)/gim, "<strong style='display:block;margin-top:0.75rem;color:#38bdf8;font-size:0.95rem;'>$1</strong>")
    .replace(/^## (.*$)/gim, "<strong style='display:block;margin-top:0.9rem;color:#818cf8;font-size:1.025rem;'>$1</strong>")
    .replace(/^# (.*$)/gim, "<strong style='display:block;margin-top:1rem;color:#c4b5fd;font-size:1.1rem;'>$1</strong>")
    // Bold — use [^*]+ to match across any char including quotes, but not across newlines
    .replace(/\*\*([^*\n]+(?:\n[^*\n]+)*?)\*\*/gim, "<strong>$1</strong>")
    // Italic
    .replace(/\*([^*\n]+)\*/gim, "<em style='color:#94a3b8;'>$1</em>")
    // Numbered lists (1. , 2. )
    .replace(/^([0-9]+)\. (.*$)/gim, "<div style='margin:0.3rem 0 0.3rem 0.6rem;display:flex;gap:0.4rem;'><strong style='color:#a5f3fc;min-width:1.2rem;'>$1.</strong><span>$2</span></div>")
    // Bullets (* or - at line start)
    .replace(/^\* (.*$)/gim, "<div style='margin:0.25rem 0 0.25rem 0.6rem;color:#f1f5f9;display:flex;gap:0.4rem;'><span style='color:#38bdf8;'>•</span><span>$1</span></div>")
    .replace(/^- (.*$)/gim, "<div style='margin:0.25rem 0 0.25rem 0.6rem;color:#f1f5f9;display:flex;gap:0.4rem;'><span style='color:#38bdf8;'>•</span><span>$1</span></div>")
    // Paragraph breaks
    .replace(/\n\n/g, "<p style='margin-bottom:0.5rem;'></p>")
    .replace(/\n/g, "<br>");

  return html;
}

function escapeHtml(text) {
  const map = { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" };
  return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * Static fallback dataset in case /api/metrics fails to load
 */
function loadStaticFallback() {
  const fallback = {
    overview: {
      total_revenue: 170820.5,
      total_units_sold: 241,
      average_transaction_value: 885.08
    },
    demographic_patterns: {
      young_adult_rev_share: 50.9,
      age_groups: [
        { age_group: "Young Adult (20-30)", rev_share: 50.9 },
        { age_group: "Adult (31-50)", rev_share: 32.7 },
        { age_group: "Senior (50+)", rev_share: 16.4 }
      ],
      payment_methods: [
        { payment_method: "UPI", share_pct: 62.2 },
        { payment_method: "Card", share_pct: 22.8 },
        { payment_method: "Cash", share_pct: 15.0 }
      ]
    },
    product_performance: {
      top_10: [
        { product_name: "Anarkali Kurta Set", units_sold: 28, revenue: 33774.0 },
        { product_name: "Slim Fit Jeans", units_sold: 26, revenue: 24775.2 },
        { product_name: "Floral Kurti", units_sold: 24, revenue: 16146.9 },
        { product_name: "Oversized Cotton T-Shirt", units_sold: 22, revenue: 10279.4 },
        { product_name: "Printed Silk Scarf", units_sold: 18, revenue: 2415.3 },
        { product_name: "Cotton Chinos", units_sold: 17, revenue: 14743.6 },
        { product_name: "Beaded Boho Earrings", units_sold: 16, revenue: 1751.2 },
        { product_name: "Classic Leather Belt", units_sold: 15, revenue: 3036.3 },
        { product_name: "Cotton Kurta Pajama", units_sold: 13, revenue: 12187.8 },
        { product_name: "Classic Polo T-Shirt", units_sold: 13, revenue: 7667.2 }
      ],
      top_3: [
        { product_name: "Anarkali Kurta Set", units_sold: 28, revenue: 33774.0 },
        { product_name: "Slim Fit Jeans", units_sold: 26, revenue: 24775.2 },
        { product_name: "Floral Kurti", units_sold: 24, revenue: 16146.9 }
      ]
    },
    weekday_analysis: {
      breakdown: [
        { day_of_week: "Monday", revenue: 26677.1, units_sold: 37, tx_count: 28 },
        { day_of_week: "Tuesday", revenue: 17033.0, units_sold: 26, tx_count: 21 },
        { day_of_week: "Wednesday", revenue: 27318.4, units_sold: 36, tx_count: 30 },
        { day_of_week: "Thursday", revenue: 18355.7, units_sold: 21, tx_count: 19 },
        { day_of_week: "Friday", revenue: 18073.2, units_sold: 26, tx_count: 23 },
        { day_of_week: "Saturday", revenue: 31728.6, units_sold: 47, tx_count: 36 },
        { day_of_week: "Sunday", revenue: 31634.5, units_sold: 48, tx_count: 36 }
      ]
    },
    size_analysis: {
      distribution: [
        { size: "L", share_pct: 26.1 },
        { size: "M", share_pct: 26.1 },
        { size: "S", share_pct: 22.4 },
        { size: "XL", share_pct: 17.0 },
        { size: "XS", share_pct: 8.3 }
      ]
    },
    discount_efficiency: {
      categories: [
        { category: "Ethnic Wear", revenue_share_pct: 38.25, avg_discount: 6.1 },
        { category: "Bottoms", revenue_share_pct: 33.09, avg_discount: 4.5 },
        { category: "Tops", revenue_share_pct: 16.63, avg_discount: 4.7 },
        { category: "Footwear", revenue_share_pct: 7.81, avg_discount: 7.1 },
        { category: "Accessories", revenue_share_pct: 4.22, avg_discount: 45.2 }
      ]
    }
  };

  populateKPIs(fallback);
  renderAllCharts(fallback);
}
