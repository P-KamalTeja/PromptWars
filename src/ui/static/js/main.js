/* Main JavaScript for Web UI */

// Form handling
document.getElementById('tripForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    await handleTripPlanSubmit();
});

document.getElementById('updateForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    await handleTripUpdateSubmit();
});

// Copy Trip ID button
document.getElementById('copyTripId')?.addEventListener('click', () => {
    const tripId = document.getElementById('tripId').textContent;
    navigator.clipboard.writeText(tripId).then(() => {
        alert('Trip ID copied to clipboard!');
    });
});

async function handleTripPlanSubmit() {
    const destination = document.getElementById('destination').value;
    const budget = parseFloat(document.getElementById('budget').value);
    const days = parseInt(document.getElementById('days').value);
    const interests = document.getElementById('interests').value;
    const travelers = parseInt(document.getElementById('travelers').value);
    const traveler_type = document.getElementById('traveler_type').value;

    // Show loading
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');
    document.getElementById('error').classList.add('hidden');

    try {
        const response = await fetch('/api/plan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                destination,
                budget,
                days,
                interests,
                travelers,
                traveler_type,
            }),
        });

        if (!response.ok) {
            const error = await readErrorResponse(response);
            throw new Error(error || 'Failed to plan trip');
        }

        const data = await response.json();

        // Display results
        document.getElementById('tripId').textContent = data.trip_id;
        document.getElementById('resultDestination').textContent = data.destination;
        document.getElementById('resultDuration').textContent = data.duration;
        document.getElementById('resultCost').textContent = data.total_cost.toFixed(2);
        document.getElementById('resultConfidence').textContent = (
            data.confidence_score * 100
        ).toFixed(1);

        document.getElementById('loading').classList.add('hidden');
        document.getElementById('results').classList.remove('hidden');

    } catch (error) {
        console.error('Error:', error);
        document.getElementById('errorMessage').textContent = error.message;
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('error').classList.remove('hidden');
    }
}

async function handleTripUpdateSubmit() {
    const tripId = document.getElementById('tripIdInput').value;
    const updateRequest = document.getElementById('updateRequest').value;

    // Show loading
    document.getElementById('updateLoading').classList.remove('hidden');
    document.getElementById('updateResults').classList.add('hidden');
    document.getElementById('updateError').classList.add('hidden');

    try {
        const response = await fetch(`/api/trips/${tripId}/update`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                update_request: updateRequest,
            }),
        });

        if (!response.ok) {
            const error = await readErrorResponse(response);
            throw new Error(error || 'Failed to update trip');
        }

        document.getElementById('updateLoading').classList.add('hidden');
        document.getElementById('updateResults').classList.remove('hidden');

    } catch (error) {
        console.error('Error:', error);
        document.getElementById('updateErrorMessage').textContent = error.message;
        document.getElementById('updateLoading').classList.add('hidden');
        document.getElementById('updateError').classList.remove('hidden');
    }
}

async function readErrorResponse(response) {
    try {
        const data = await response.json();
        return data.error;
    } catch {
        return await response.text();
    }
}

// Smooth navigation
document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener('click', (e) => {
        const href = link.getAttribute('href');
        if (href !== '#' && href !== '') {
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
                // Update active nav link
                document.querySelectorAll('.nav-link').forEach((n) => {
                    n.classList.remove('active');
                });
                link.classList.add('active');
            }
        }
    });
});
