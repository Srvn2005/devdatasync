const request = require('supertest');
const app = require('../server'); // Make sure to export app from server.js

describe('POST /api/auth/login', () => {
  it('should return 400 if no credentials are provided', async () => {
    const res = await request(app).post('/api/auth/login').send({});
    expect(res.statusCode).toBe(400);
  });
});
