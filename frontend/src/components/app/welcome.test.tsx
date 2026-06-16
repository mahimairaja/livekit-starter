import { render, screen } from "@testing-library/react";
import { expect, test, vi } from "vitest";
import { Welcome } from "@/components/app/welcome";

test("welcome screen shows a start button", () => {
  render(<Welcome onStart={vi.fn()} />);
  expect(
    screen.getByRole("button", { name: /start conversation/i }),
  ).toBeInTheDocument();
});

test("welcome screen surfaces failure reasons", () => {
  render(<Welcome onStart={vi.fn()} failureReasons={["network error"]} />);
  expect(screen.getByText(/network error/i)).toBeInTheDocument();
});
