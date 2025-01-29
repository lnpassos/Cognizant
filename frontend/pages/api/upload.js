import axios from 'axios';

export default async function handler(req, res) {
    if (req.method === 'POST') {
        try {
            const response = await axios.post('http://localhost:8000/files/upload', req.body, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            res.status(200).json(response.data);
        } catch (error) {
            res.status(500).json({ message: 'Error uploading file' });
        }
    } else {
        res.status(405).json({ message: 'Method Not Allowed' });
    }
}
