const video = document.getElementById("video");
const msg = document.getElementById("message");
let counter = 0;

const data = {
	"tilak.dave22": {
		"count": 0,
		"happy": 0,
		"neutral": 0,
		"angry": 0,
		"sad": 0,
		"fearful": 0,
		"disgusted": 0,
		"surprised": 0,
		"sentences": []
	},
	"akash.deshmukh22": {
		"count": 0,
		"happy": 0,
		"neutral": 0,
		"angry": 0,
		"sad": 0,
		"fearful": 0,
		"disgusted": 0,
		"surprised": 0,
		"sentences": []
	},
	"siddhesh.shinde22": {
		"count": 0,
		"happy": 0,
		"neutral": 0,
		"angry": 0,
		"sad": 0,
		"fearful": 0,
		"disgusted": 0,
		"surprised": 0,
		"sentences": []
	},
	"soham.dixit22": {
		"count": 0,
		"happy": 0,
		"neutral": 0,
		"angry": 0,
		"sad": 0,
		"fearful": 0,
		"disgusted": 0,
		"surprised": 0,
		"sentences": []
	},
}


function handleSubmit() {
	console.log("submit");
	// make an api request and pass data to 127.0.0.1:5000/api
	fetch("http://127.0.0.1:5000/api", {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(data),
	})
		.then((response) => response.json())
		.then((data) => {
			console.log("Success:", data);
		}
		)
		.catch((error) => {
			console.error("Error:", error);
		}
		);
}


Promise.all([
	faceapi.nets.tinyFaceDetector.loadFromUri("/static/models"),
	faceapi.nets.faceLandmark68Net.loadFromUri("/static/models"),
	faceapi.nets.faceRecognitionNet.loadFromUri("/static/models"),
	faceapi.nets.faceExpressionNet.loadFromUri("/static/models"),
	faceapi.nets.ssdMobilenetv1.loadFromUri("/static/models"),
]).then(startVideo);

async function startVideo() {
	navigator.getUserMedia(
		{ video: { width: 600, height: 400 } },
		(stream) => (video.srcObject = stream),
		(err) => console.error(err)
	);
}

video.addEventListener("play", async () => {
	const labeledFaceDescriptors = await loadLabeledImages();
	const faceMatcher = new faceapi.FaceMatcher(labeledFaceDescriptors, 0.6);
	const canvas = faceapi.createCanvasFromMedia(video);
	document.body.append(canvas);
	const displaySize = { width: video.width, height: video.height };
	faceapi.matchDimensions(canvas, displaySize);
	const intervalID = setInterval(async () => {
		if (counter >= 30) {
			clearInterval(intervalID);
			handleSubmit();
		}
		counter++;
		console.log(counter);
		const detections = await faceapi
			.detectAllFaces(video)
			.withFaceLandmarks()
			.withFaceExpressions()
			.withFaceDescriptors();
		const resizedDetections = faceapi.resizeResults(detections, displaySize);
		canvas.getContext("2d").clearRect(0, 0, canvas.width, canvas.height);
		// faceapi.draw.drawDetections(canvas, resizedDetections);
		// faceapi.draw.drawFaceExpressions(canvas, resizedDetections);

		const results = resizedDetections.map((d) =>
			faceMatcher.findBestMatch(d.descriptor)
		);
		results.forEach((result, i) => {
			data[ result.toString().slice(0, -7) ][ "count" ]++;
			data[ result.toString().slice(0, -7) ][ "sentences" ].push(msg.textContent);
			const box = resizedDetections[ i ].detection.box;
			const drawBox = new faceapi.draw.DrawBox(box, {
				label: result.toString(),
			});

			drawBox.draw(canvas);
			for (const key in resizedDetections[ 0 ].expressions) {
				if (resizedDetections[ 0 ].expressions[ key ] > 0.77) {
					console.log(`${key}: ${resizedDetections[ 0 ].expressions[ key ]}`);
					data[ result.toString().slice(0, -7) ][ `${key}` ]++;
				}
			}
		});
		console.log(data);
	}, 1000); y
});

function loadLabeledImages() {
	const labels = [
		"tilak.dave22",
		"akash.deshmukh22",
		"siddhesh.shinde22",
		"soham.dixit22",
	];
	return Promise.all(
		labels.map(async (label) => {
			const descriptions = [];
			for (let i = 1; i <= 2; i++) {
				const img = await faceapi.fetchImage(
					`https://firebasestorage.googleapis.com/v0/b/stealth-mode-18b16.appspot.com/o/${label}%2F${i}.jpg?alt=media`
				);
				const detections = await faceapi
					.detectSingleFace(img)
					.withFaceLandmarks()
					.withFaceDescriptor();
				descriptions.push(detections.descriptor);
			}
			return new faceapi.LabeledFaceDescriptors(label, descriptions);
		})
	);
}
