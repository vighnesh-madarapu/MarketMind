
document.addEventListener("DOMContentLoaded", function () {

    // =====================================
    // MARKETMIND ANALYTICS CHARTS
    // =====================================

    const dataElement = document.getElementById("analytics-data");

    if (!dataElement || typeof Chart === "undefined") {
        return;
    }

    let data;

    try {
        data = JSON.parse(dataElement.textContent);
    } catch (error) {
        console.error("Unable to read analytics data:", error);
        return;
    }

    // Safely prepare chart data
    const labels = Array.isArray(data.labels) && data.labels.length
        ? data.labels
        : ["No campaign data"];

    const hasCampaigns = Array.isArray(data.labels) && data.labels.length > 0;

    const impressions = hasCampaigns ? data.impressions : [0];
    const clicks = hasCampaigns ? data.clicks : [0];
    const conversions = hasCampaigns ? data.conversions : [0];
    const revenue = hasCampaigns ? data.revenue : [0];

    // Common chart settings
    Chart.defaults.font.family = "DM Sans, sans-serif";
    Chart.defaults.color = "#7e8493";

    // =====================================
    // CAMPAIGN PERFORMANCE CHART
    // =====================================

    const performanceCanvas = document.getElementById("performanceChart");

    if (performanceCanvas) {

        new Chart(performanceCanvas, {
            type: "bar",

            data: {
                labels: labels,

                datasets: [
                    {
                        label: "Impressions",
                        data: impressions,
                        backgroundColor: "#a99dcc",
                        borderRadius: 5,
                        maxBarThickness: 45
                    },
                    {
                        label: "Clicks",
                        data: clicks,
                        backgroundColor: "#8da99a",
                        borderRadius: 5,
                        maxBarThickness: 45
                    },
                    {
                        label: "Conversions",
                        data: conversions,
                        backgroundColor: "#d4b98c",
                        borderRadius: 5,
                        maxBarThickness: 45
                    }
                ]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                interaction: {
                    intersect: false,
                    mode: "index"
                },

                plugins: {
                    legend: {
                        position: "bottom",
                        labels: {
                            usePointStyle: true,
                            padding: 18
                        }
                    },

                    tooltip: {
                        backgroundColor: "#202943",
                        padding: 12,
                        cornerRadius: 8
                    }
                },

                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: "#eeeeF3"
                        }
                    },

                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });

    }

    // =====================================
    // CAMPAIGN REVENUE CHART
    // =====================================

    const revenueCanvas = document.getElementById("revenueChart");

    if (revenueCanvas) {

        new Chart(revenueCanvas, {
            type: "bar",

            data: {
                labels: labels,

                datasets: [
                    {
                        label: "Revenue (₹)",
                        data: revenue,
                        backgroundColor: "#8da99a",
                        borderRadius: 6,
                        maxBarThickness: 55
                    }
                ]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        display: false
                    },

                    tooltip: {
                        backgroundColor: "#202943",
                        padding: 12,
                        cornerRadius: 8,

                        callbacks: {
                            label: function (context) {
                                return "Revenue: ₹" +
                                    Number(context.raw || 0).toLocaleString("en-IN");
                            }
                        }
                    }
                },

                scales: {
                    y: {
                        beginAtZero: true,

                        grid: {
                            color: "#eeeeF3"
                        },

                        ticks: {
                            callback: function (value) {
                                return "₹" + Number(value).toLocaleString("en-IN");
                            }
                        }
                    },

                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });

    }

});
